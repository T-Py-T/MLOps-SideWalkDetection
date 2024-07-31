# removeLowVelocityImages -- Move images with velocity below threshold into separate folder
#
# removeLowVelocityImages.py inputFolder [thresh]
#
#   thresh:  velocity threshold in rpm
#
import os
import sys
import numpy as np

default_vel_thresh = 10

# Define raw data and output file formats 
rawf = {'frame' : 0, 'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'joy' : 18}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
# Define class_results file formats 
resf = {'frame' : 0, 'label' : 1}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}


# Get input parameters from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('Input Folder Missing')
    
    
if len(sys.argv) > 2:
        vel_thresh = float(sys.argv[2])
else:
    vel_thresh = default_vel_thresh
    
 # get class labels from dictionary
labels = []
keys = label_dict.keys() 
for label in keys:
    labels.append(label)
num_classes = len(labels)
    
# create folder for low-vel images
if not os.path.exists(dirIn + 'low_vel'):
    os.mkdir(dirIn + 'low_vel')
    
# load data files into arrays
if os.path.exists(dirIn + 'out_data.txt'):
    out = np.genfromtxt(dirIn + 'out_data.txt', delimiter=',')
else:
    raise Exception('Unable to load data file')
if os.path.exists(dirIn + 'raw_data.txt'):
    try:
        raw = np.genfromtxt(dirIn + 'raw_data.txt', delimiter=',')
    except:
        print('\n Unable to read raw data file \n')

# pull data from arrays
img_nums = out[:, outf['frame']]
num_images = len(img_nums)
odo = raw[:, rawf['odo']]

# get list of images in input folder    
fnames = sorted([fname for fname in os.listdir(dirIn)])

# loop through images
for file in fnames:

    if file[-4:] != '.jpg':
        continue
    
    try:
        img_num = int(file[-9:-4])  # get image number from file name 
        #img_num = int(file[-19:-13] + file[-12:-10] + file[-9:-4])
        ix = np.where(img_nums==img_num)[0][0] # find image in summary file
    except:
        print(file,img_num)
        continue


    if  odo[ix] < vel_thresh:
        os.rename(dirIn + file, dirIn + 'low_vel/' + file)
 
    print(file)

    
        
        
    

