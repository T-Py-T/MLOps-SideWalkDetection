# makeLPRvideo.py --  Combine images from scooter with LPR data
#                         to create video
import os
import cv2, sys
import numpy as np
import time
import pandas as pd

# define image classifier thresholds for sidewalk detection
sw_thresh = 0.6
street_thresh = 0.6
inter_thresh = 0.6
sw_filt_len = 6

# Define raw data and output file formats 
rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'joy' : 18}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'back' : 0, 'intersect' : 1, 'side' : 2, 'street' : 3}



print("\n\nPress 'q' to quit, or <space> to pause/continue\n\n")

# Check command line arguments
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
else:
    raise Exception('Input Folder Missing')
    
    
# load files into arrays
try:
    out = np.genfromtxt(dirIn + '/out_data.txt', delimiter=',')
except:
    raise Exception('Data Output File not found')
if os.path.exists(dirIn + '/raw_data.txt'):    
    raw = np.genfromtxt(dirIn + '/raw_data.txt', delimiter=',')
else:
    raw = np.zeros((len(out),rawf['joy']+1))

# pull data from arrays
img_nums_class = out[:, outf['frame']]
inter_scores = out[:, outf['class'] + label_dict['intersect']]
sw_scores = out[:, outf['class'] + label_dict['side']]
street_scores = out[:, outf['class'] + label_dict['street']]
joy_inputs = raw[:, rawf['joy']]


my_cols = ['c' + str(i) for i in range(34)]
lpr = pd.read_csv(dirIn + '/lpr_data.txt', sep=',|:', 
                  names = my_cols)
num_img = len(lpr.c1)

img_nums = lpr.c3
plates = lpr.c9
conf = np.zeros(num_img)
box0 = np.zeros(num_img)
box7 = np.zeros(num_img)
for i in range(num_img):
    if lpr.c6[i] != None:
        conf[i] = float(lpr.c6[i][1:])
        box0[i] = float(lpr.c11[i][1:])
        box7[i] = float(lpr.c18[i][:-4])
box = np.vstack(([box0, lpr.c12], [lpr.c13, lpr.c14],
                 [lpr.c15, lpr.c16], [lpr.c17, box7]))

box = np.transpose(box)


# Define the codec and create VideoWriter object for output video
videoFileOut=dirIn + '/' + os.path.basename(dirIn) + '.mp4'
fps=5.0;
(w,h) = (int(1648/2), int(1232/2))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
videoOut = cv2.VideoWriter(videoFileOut,fourcc, fps, (w,h))
font = cv2.FONT_HERSHEY_SIMPLEX

# get list of images in input folder
fnames = sorted([fname for fname in os.listdir(dirIn)])

# loop through images
for file in fnames:
    print(file)
    if file[-4:] != '.jpg':
        continue
    frame=cv2.imread(dirIn + '/' + file)

#    # find image data in output file
    img_num = int(file[-9:-4])
    #img_num = int(file[-13:-9])
    try:
        ix = np.where(img_nums == img_num)[0][0]
    except:
        ix = 0
        box[ix][0] = 0
    
    pts = box[ix]
    if pts[0] != 0:
        pts = np.array([[pts[0],pts[1]],[pts[2],pts[3]],
                        [pts[4],pts[5]],[pts[6],pts[7]]], np.int32)
        pts = pts.reshape((-1,1,2))
        
        
        # add box with plate number
        labelSize=cv2.getTextSize(plates[ix][1:-1],font,1.0,2)
        r1 = (pts[3][0][0], pts[3][0][1])
        r2 = (pts[3][0][0] + labelSize[0][0], pts[2][0][1] + labelSize[0][1]*2)
        if conf[ix] > 60:
            cv2.polylines(frame, [pts], True, (0,255,0), thickness=2)
            cv2.rectangle(frame,r1,r2,(0,255,0),cv2.FILLED)
        else:
            cv2.polylines(frame, [pts], True, (0,255,255), thickness=2)
            cv2.rectangle(frame,r1,r2,(0,255,255),cv2.FILLED)
    
    
        # add plate number to image  
        cv2.putText(frame, plates[ix][1:-1], 
                    (pts[3][0][0],pts[3][0][1]+30), font, 1.0, (0,0,0), 2, cv2.LINE_AA)
        print('Plate: %s Conf: %.1f' % (plates[ix][1:-1], conf[ix]))


    # add frame number to image  
    cv2.putText(frame, 'FRAME = ' + str(img_num), 
                (w-140,40), font, 0.5, (0,0,0), 2, cv2.LINE_AA)


    #img_num = int(file[-9:-4])
    try:
        ix2=np.where(img_nums_class == img_num)[0][0]
    except:
        continue
    
    # add boxes to image
    ixfilt = range(ix2 - sw_filt_len + 1, ix2 + 1) 

    if np.mean(inter_scores[ixfilt]) > inter_thresh:
        cv2.rectangle(frame, (1,1), (w*2-1,h-1), (0,255,255), 3) # yellow box
    elif np.mean(street_scores[ixfilt]) > street_thresh:
        cv2.rectangle(frame, (1,1), (w*2-1,h-1), (0,255,0), 3) # green box
    elif np.mean(sw_scores[ixfilt]) > sw_thresh:
        cv2.rectangle(frame, (1,1), (w*2-1,h-1), (0,0,255), 3) # red box



    
    # resize and display frame
    frame = cv2.resize(frame, (w,h), interpolation = cv2.INTER_AREA)
    cv2.imshow('frame',frame)


    # write image to video
    videoOut.write(frame)
    if box[ix][0] != 0:
        for i in range(5): 
            videoOut.write(frame)

    time.sleep(0.02)

    # check for user pause or quit
    key=cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # quit
        break 
    elif key == ord(' '):  #pause
        cv2.waitKey(0)
        
    if box[ix][0] != 0:
        time.sleep(1.5)



videoOut.release()
cv2.destroyAllWindows()