# scooter.py -- Sample images/data from camera/gps/imu or from file set, classify the images
#                   determine position and velocity, and save results, also support LPR and wifi sniffing
#
#            python3 scooter.py -options fileDir
#	
#			 options: -S = limit speed, -W=enable wifi, -L=enable LPR, -F= post-process files, -SWL = do all three
#            fileDir:  folder of images and results for post-processing

from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
import cv2
import numpy as np
import time, sys, os, math
import serial
import pynmea2
import nectar
from em7180 import EM7180_Master
import re

from cnn import CNN              # neural network interface

############## Defines ###########################################

# Specify the neural network model and image size
modelFile = 'models/mobileV2_denver_0303.tflite'

# Specify LPR interface
lprDir = '/var/ramdisk'
lpr_results_file = lprDir + "/lpr_data.txt"

# set speed control parameters
MAX_SIDEWALK_SPEED = 0.160 # krpm, ~4 mph
MAX_SPEED          = 0.600 # krpm, ~15 mph
DELTA_SPEED        = (MAX_SPEED - MAX_SIDEWALK_SPEED) / (10 * 3) # krpm, speed reduction per sample (10 sec at 3 samp/sec)

# set camera image parameters
videoPortMode = True             # True=video, False=still
lpr_imageSize = (1648, 1232)	 # size of lpr image
classify_imageSize = (640, 480)  # image resize for classifier
cam_crop = (80, 560, 0, 480)	 # region of classify image to use for classification
lpr_crop = (0, 1648, 500, 1100)  # region of cam image to use for lpr

# define GPIO by pin #, new black box
ledGreen = 18 
ledRed = 17 
joyHoriz = 23 
joyVert = 24 
push1 = 19 

# define serial ports
GPS_DEVICE_PATH = '/dev/ttyAMA2'
GPS_BAUD = 115200
MP2_DEVICE_PATH = '/dev/ttyAMA4'
	
# define image classes, these must be alphabetical to match keras API
#label_dict = {'intersect' : 0, 'side' : 1, 'street' : 2}  # for models pre 3/3
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}


filtLen = 6			# length of running average filter for classifier outputs
swThresh = 0.5		# classifier threshold for sidewalk detection 
streetThresh = 0.5	# classifier threshold for street detection

# setup for IMU
MAG_RATE       = 100  # Hz
ACCEL_RATE     = 200  # Hz
GYRO_RATE      = 200  # Hz
BARO_RATE      = 50   # Hz
Q_RATE_DIVISOR = 3    # 1/3 gyro rate


# Define raw data and output file formats
rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'speed' : 17, 'joy' : 18}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}

rawfile_format = '%5s,%9.2f,' + 2 * '%14.9f,' + '%9.2f,' + 13 * '%5.2f,' + '%d\n'
outfile_format = '%5s,%d,' + 6 * '%3.2f,' + '%d,' + 3 * '%14.9f,' + 3 * '%5.2f,' + '\n'

# Check command line arguments for data set folder or max sidewalk speed

camFlag = True
limit_sidewalk_speed = wifi_enabled = lpr_enabled = False
if len(sys.argv) > 1:
	if sys.argv[1].find('L') > 0:
		lpr_enabled = True
	if sys.argv[1].find('S') > 0:
		limit_sidewalk_speed = True
if len(sys.argv) > 2:
		print('Run in post-process mode ...')
		dirIn = sys.argv[2]
		dirOut = str(sys.argv[2])
		camFlag = False


############## Functions #########################################

def get_raw_data(MP2, GPS, IMU):

	# get MP2 odometer speed
	try:
		speed = MP2.get_observed_speed()
	except:
		speed = 0
		print('Error: Unable to read MP2 speed') 

	# get GPS position
	gps = [0] * 6
	try:
		str = GPS.readline().decode(errors='replace')
		GPS.reset_input_buffer()	# don't let buffer fill up
	except:
		print('Error: Unable to read GPS')

	if str.find('GGA') > 0:
		try:
			msg = pynmea2.parse(str)
			gps[0] = msg.latitude
			gps[1] = msg.longitude
			gps[2] = float(msg.altitude)
		except:
			pass
	
	# get joystick input
	try:
		joy = (1-GPIO.input(joyHoriz)) + 2 * (1-GPIO.input(joyVert))
	except:
		print('Error: Unable to read joy stick')

	# get IMU measurements
	imu = [0] * 9
	try:
		IMU.checkEventStatus()
		if IMU.gotError():
			print('ERROR: ' + IMU.getErrorString())
		if (IMU.gotQuaternion()):
			qw, qx, qy, qz = IMU.readQuaternion()
			roll  = math.atan2(2.0 * (qw * qx + qy * qz), qw * qw - qx * qx - qy * qy + qz * qz)
			pitch = -math.asin(2.0 * (qx * qz - qw * qy))
			yaw   = math.atan2(2.0 * (qx * qy + qw * qz), qw * qw + qx * qx - qy * qy - qz * qz)   
			pitch *= 180.0 / math.pi
			yaw   *= 180.0 / math.pi 
			yaw   += 8.0 # Declination at Denver,CO
			if yaw < 0: yaw   += 360.0  # Ensure yaw stays between 0 and 360
			roll  *= 180.0 / math.pi
			imu[0], imu[1], imu[2] = yaw, pitch, roll
		if IMU.gotAccelerometer():
			imu[3], imu[4], imu[5] = IMU.readAccelerometer()
		if IMU.gotGyrometer():
			imu[6], imu[7], imu[8] = IMU.readGyrometer()
	except:
		print('Error: Unable to read IMU')

	return (gps, imu, speed, joy)


def get_raw_data_from_buffer(rawData, frame_num):
	try:
		ix = np.where(rawData[:,0] == int(frame_num))[0][0]
		gps = rawData[ix, rawf['gps']:rawf['gps'] + 5]
		imu = rawData[ix, rawf['imu']:rawf['imu'] + 8]
		speed = rawData[ix, rawf['speed']]
		joy = rawData[ix, rawf['joy']]
	except:
		gps = [-1] * 6
		imu = [-1] * 9
		speed = -1
		joy = -1 

	return (gps, imu, speed, joy)

def est_pos(gps, imu, speed):
	# estimate position- just use raw gps for now, later 
	# add imu and odometer speed
	pos = gps[0:2]
	vel = gps[3:5]
	return (pos, vel)

	
############## Start of main code #################################

def main():

	global dirOut   # allows variable to be changed within main()

	# initialize the neural network
	cnn = CNN(modelFile)

	# delete old images on ram disk
	files = os.listdir(lprDir)
	for file in files:
		if file.endswith(".jpg") or file.endswith(".txt"):
			os.remove(os.path.join(lprDir,file))
	
	# intialize camera or input files 
	if camFlag:
		# initialize the camera and grab a reference to the raw camera capture
		if lpr_enabled:
			cam_imageSize = lpr_imageSize
		else:
			cam_imageSize = classify_imageSize
		camera = PiCamera()
		camera.resolution = cam_imageSize 
		camera.framerate = 10
		camera.vflip = False
		camera.hflip = False
		rawCapture = PiRGBArray(camera, size=cam_imageSize)
	else:
		# initialize files
		fnames = sorted([fname for fname in os.listdir(dirIn)])

	# initialize GPIO
	GPIO.setwarnings(False) # Ignore warning for now
	GPIO.setmode(GPIO.BCM) # Use physical pin numbering
	GPIO.setup(ledGreen, GPIO.OUT, initial=GPIO.LOW) # green LED
	GPIO.setup(ledRed, GPIO.OUT, initial=GPIO.HIGH) # red LED
	GPIO.setup(joyHoriz, GPIO.IN,GPIO.PUD_DOWN) # joystick horiz axis
	GPIO.setup(joyVert, GPIO.IN,GPIO.PUD_DOWN) # joystick vert axis
	GPIO.setup(push1, GPIO.IN,GPIO.PUD_UP) # push button

	GPIO.output(ledGreen, GPIO.LOW)
	GPIO.output(ledRed, GPIO.LOW)

	if camFlag:
		# intialize MP2 motor controller interface
		try:
			MP2 = nectar.Controller(MP2_DEVICE_PATH)
			if limit_sidewalk_speed:
				current_max_speed =  MAX_SIDEWALK_SPEED
			else:
				current_max_speed = MAX_SPEED
			last_max_speed = 0
			MP2.set_speed(current_max_speed)	
		except serial.SerialException:
			print('Unable to connect MP2 to {}, SerialException'.format(MP2_DEVICE_PATH))
			return(0)

		# initialize GPS module
		try:
			GPS = serial.Serial(GPS_DEVICE_PATH, baudrate = GPS_BAUD, timeout = 0)
		except serial.SerialException:
			print('Unable to connect GPS to {}, SerialException'.format(GPS_DEVICE_PATH))
			return(0)

		# intialize IMU
		IMU = EM7180_Master(MAG_RATE, ACCEL_RATE, GYRO_RATE, BARO_RATE, Q_RATE_DIVISOR)
		# Start the EM7180 in master mode
		if not IMU.begin():
			print(IMU.getErrorString())
			return(0)
	
	# initialize output data
	pos = [0] * 3   # best estimate of position based on multiple sensors
	vel = [0] * 3   # best estimate of velocity based on multiple sensors
	sw_preds = [0] * filtLen		# rolling buffer of sidewalk classifier outputs
	street_preds = [0] * filtLen	# rolling buffer of street classifier outputs

	# wait for LPR process to open results file
	while(1):
		if lpr_enabled == False:
			break	                                
		try:
			lprIn = open(lpr_results_file,"r")
			break
		except:
			print('Waiting for LPR process ...')
			time.sleep(1)

	# initialize main loop
	time0 = time.time()
	frame_num = 0
	
	np.set_printoptions(precision=2)
	
	# start main loop
	while True:
		# wait for button push to start recording if running camera
		while camFlag == True:
			GPIO.output(ledRed, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(ledRed, GPIO.LOW)
			time.sleep(0.5)
			if 1: #GPIO.input(push1) == 0:   # ----- change this line to disable push button ------
				time.sleep(1)
				# create new output folder
				dirs=next(os.walk('.'))[1]
				run_num = 1
				while True:
					dirOut = "run" + str(run_num)
					if dirOut not in dirs:
						break
					run_num +=1
				os.mkdir(dirOut)
				break
	
		# Open raw data and output data files
		outFile = open(dirOut +"/out_data.txt","w")
		if camFlag:
			rawFile =  open(dirOut +"/raw_data.txt","w")
	
	####################### real-time input from camera ######################################################
	
		if camFlag:  # capture frames from the camera, save and classify
			#t0=time.time()
			for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=videoPortMode):
				
				# Turn on status LED
				GPIO.output(ledGreen, GPIO.HIGH)
			
				# grab the raw NumPy array representing the image
				image = frame.array
				rawCapture.truncate(0)  # clear the stream in preparation for the next frame
				
				if lpr_enabled:
					# save lpr cropped image to ramdisk and resize image for classifier
					image_lpr = image[lpr_crop[2]:lpr_crop[3], lpr_crop[0]:lpr_crop[1]]
					cv2.imwrite(lprDir +"/img_" + str(frame_num).zfill(5) + ".jpg", image_lpr)
					image = cv2.resize(image, classify_imageSize, interpolation=cv2.INTER_AREA)
				else:
					# save image to output folder
					cv2.imwrite(dirOut +"/img_" + str(frame_num).zfill(5) + ".jpg", image)

				# crop image for classification
				image_classify = image[cam_crop[2]:cam_crop[3], cam_crop[0]:cam_crop[1]]

				# classify image
				imclass = cnn.classify_image(image_classify)
				#print(time.time()-t0)
				label = np.argmax(imclass)
	
				# Turn off status LED
				GPIO.output(ledGreen, GPIO.LOW)
				
				# add classifier results to rolling buffers
				sw_preds.pop(0)
				street_preds.pop(0)
				sw_preds.append(max(imclass[label_dict['side']], imclass[label_dict['crosswalk']]))
				street_preds.append(max(imclass[label_dict['street']], imclass[label_dict['bike_lane']]))
		
				# calculate rolling averages from classifer
				sw_avg = sum(sw_preds[-filtLen:]) / filtLen
				street_avg = sum(street_preds[-filtLen:]) / filtLen
	                        			
				# get raw data from gps, imu, mp2, and joystick
				t0=time.time()
				(gps, imu, speed, joy) = get_raw_data(MP2, GPS, IMU)
	
				# estimate position and velocity from gps, imu, and mp2 data
				(pos, vel) = est_pos(gps, imu, speed)
	
				# check for sidewalk and output status to LED
				if sw_avg > swThresh and street_avg < streetThresh:   
					GPIO.output(ledRed, GPIO.HIGH) # Turn on LED
					swFlag = 1
					if limit_sidewalk_speed:
						current_max_speed = max(speed - DELTA_SPEED, MAX_SIDEWALK_SPEED)
				else:
					GPIO.output(ledRed, GPIO.LOW) # Turn off LED
					swFlag = 0
					if limit_sidewalk_speed:
						current_max_speed = max(MAX_SIDEWALK_SPEED, min(speed + DELTA_SPEED, MAX_SPEED))

				# limit max scooter speed if option enabled
				if limit_sidewalk_speed and current_max_speed != last_max_speed:
					try:
						MP2.set_speed(current_max_speed)
						print('MP2 speed cmd: %.1f %.1f %d, pass' % (speed*1000, current_max_speed*1000, swFlag))	
					except:
						print('MP2 speed cmd: %.1f, fail' % current_max_speed)
				last_max_speed = current_max_speed						
	
				# display rolling averages, joystick, speed, and output LED status to screen
				print("Classifier: %5d: ST=%3.2f SW=%3.2f CW=%3.2f BL=%3.2f JS=%d %5.2f %5.2f %d" % (frame_num, 
					imclass[label_dict['street']], imclass[label_dict['side']], 
					imclass[label_dict['crosswalk']], imclass[label_dict['bike_lane']],
					joy, speed*1000, current_max_speed*1000, swFlag))
								
				# save raw inputs to file: (frame, sec, gps[6], imu[9], speed, joy)
				rawFile.write(rawfile_format % (str(frame_num).zfill(5), time.time()-time0, 
					gps[0], gps[1], gps[2], gps[3], gps[4], gps[5], imu[0], imu[1], imu[2],
					imu[3],	imu[4], imu[5], imu[6], imu[7], imu[8], speed*1000, joy)) 
				
				# save output data to file: (frame, label, imclass[6], swFlag, pos[3], vel[3])
				outFile.write(outfile_format % (str(frame_num).zfill(5), joy, imclass[0], imclass[1], 
					imclass[2], imclass[3], 0, 0, swFlag, 0, 0, 0, 0, 0, 0))

				
				frame_num += 1
				
				# check push button for end of data collection
				if GPIO.input(push1) == 0:
					outFile.close()
					rawFile.close()
					GPIO.output(ledGreen, GPIO.LOW)
					GPIO.output(ledRed, GPIO.LOW)
					time.sleep(1)
					while GPIO.input(push1) == 0:
						pass
					break
	
	####################### post-process input from files ######################################################
	
		else:  # load images from input folder and classify
	
			# get imu, gps, mp2, and switch raw data from file
			try:
				rawData = np.genfromtxt(dirOut + '/raw_data.txt', 
					delimiter=',')
			except:
				rawData = np.zeros((len(fnames), rawf['joy']))
	
			for file in fnames:
				if file[-4:] != '.jpg':
					continue
				
				frame_num = file[-9:-4]  # get image number from file name
		
				# read image	
				image = cv2.imread(dirIn+'/' + file)
				h, w, c = image.shape

				# crop image for classification if raw camera image
				if w == classify_imageSize[0]:
					image = image[cam_crop[2]:cam_crop[3], cam_crop[0]:cam_crop[1]]
		
				# classify image
				imclass = cnn.classify_image(image)
				label = np.argmax(imclass)
	
				# add classifier results to rolling buffers
				sw_preds.pop(0)
				street_preds.pop(0)
				sw_preds.append(imclass[label_dict['side']])
				street_preds.append(imclass[label_dict['street']])
		
				# calculate rolling averages from classifer
				sw_avg = sum(sw_preds[-filtLen:]) / filtLen
				street_avg = sum(street_preds[-filtLen:]) / filtLen
	
				# get raw data from buffer
				(gps, imu, speed, joy) = get_raw_data_from_buffer(rawData, frame_num)
	
				# estimate position and velocity from gps, imu, and mp2 data
				(pos, vel) = est_pos(gps, imu, speed)
	
				# check for sidewalk and output status to LED
				if sw_avg > swThresh and street_avg < streetThresh:   
					GPIO.output(ledRed, GPIO.HIGH) # Turn on LED
					swFlag = 1
				else:
					GPIO.output(ledRed, GPIO.LOW) # Turn off LED
					swFlag = 0
	
				# display rolling averages, joystick and output LED status to screen
				print("Classifier: %s: ST=%3.2f SW=%3.2f CW=%3.2f JS=%d %d" % (frame_num, 
					imclass[label_dict['street']], imclass[label_dict['side']], 
					imclass[label_dict['crosswalk']], joy, swFlag))
							
				# save output data to file: (frame, label, imclass[6], swFlag, pos[3], vel[3])
				outFile.write(outfile_format % (frame_num, joy, 0, imclass[0], 
					imclass[1], imclass[2], 0, 0, swFlag, 0, 0, 0, 0, 0, 0))

	
		# all done, close file and exit
		GPIO.output(ledRed, GPIO.LOW) # Turn off LED
		outFile.close()
		if camFlag:
			camera.close()
			MP2.disconnect()
			GPS.close()
		return(camFlag)


while(1):
	try:
		res = main()
	except:
		print("Error in main():", sys.exc_info()[0])
		raise
	if res == 0:
		break
