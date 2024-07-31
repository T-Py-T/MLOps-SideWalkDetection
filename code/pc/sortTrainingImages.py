# sortTrainingImages -- Sort images downloaded from scooter by classifier results
#
# sortLabeledImages.py inputFolder [thresh]

#
#   thresh:  threshold for high confidence classifer score
#
# Images will be moved to sub-folders inside the input folder.  Sub-folder names
# without leading underscores contain images with agreement between joystick
# label and classifier.  Leading underscore in the sub-folder name indicates 
# the two classifications did not agree or classifier score was below threshold.
# These should be manually sorted

import os
import sys
import numpy as np

# Define raw data and output file formats 
rawf = {'frame' : 0, 'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'joy' : 18}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'back' : 0, 'intersect' : 1, 'side' : 2, 'street' : 3}


# Get input parameters from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('Input Folder Missing')
    
    
if len(sys.argv) > 2:
    score_thresh = float(sys.argv[3])
else:
    score_thresh = 0.5
    
 # get class labels from dictionary
labels = []
keys = label_dict.keys() 
for label in keys:
    labels.append(label)
num_classes = len(labels)
    
# create sub-folders with class labels
for label in labels:
    if not os.path.exists(dirIn + label):
        os.mkdir(dirIn + label)  # folder for high confidence images
    if not os.path.exists(dirIn + '_' + label):
        os.mkdir(dirIn + '_' + label)  # temp folder for low confidence images

    
# load data files into arrays
if os.path.exists(dirIn + 'out_data.txt'):
    out = np.genfromtxt(dirIn + 'out_data.txt', delimiter=',')
    img_names = np.genfromtxt(dirIn + 'out_data.txt', delimiter=',', usecols=0, dtype=str)
else:
    raise Exception('Unable to load data file')
if os.path.exists(dirIn + 'raw_data.txt'):
    out = np.genfromtxt(dirIn + 'raw_data.txt', delimiter=',')
else:
    raw = np.zeros((len(out),rawf['joy']+1))

# pull data from arrays
#img_names = out[:, outf['frame']]
num_images = len(img_names)

scores = np.zeros((num_images, num_classes))
for n in range(num_classes):
    scores[:, n] = out[:, outf['class'] + n]
    
joy_inputs = raw[:, rawf['joy']]
max_ix = min(len(img_names), len(joy_inputs)) - 1

# get list of images in input folder    
fnames = sorted([fname for fname in os.listdir(dirIn)])

# loop through images
for file in fnames:

    if file[-4:] != '.jpg':
        continue
    
    try:
        ix=np.where(img_names==file)[0][0] # find image in summary file
    except:
        continue


    # if max classifier score is above threshold, put directly in final
    # folders, else put in temp folders
    if scores[ix,:].argmax() == label_dict['intersect']:
        if scores[ix,:].max() > score_thresh:
            os.rename(dirIn + file, dirIn + 'intersect/' + file)
        else:
            os.rename(dirIn + file, dirIn + '_intersect/' + file)
            
    if scores[ix,:].argmax() == label_dict['street']:
        if scores[ix,:].max() > score_thresh:
            os.rename(dirIn + file, dirIn + 'street/' + file)
        else:
            os.rename(dirIn + file, dirIn + '_street/' + file)
            
    if scores[ix,:].argmax() == label_dict['side']:
        if scores[ix,:].max() > score_thresh:
            os.rename(dirIn + file, dirIn + 'side/' + file)
        else:
            os.rename(dirIn + file, dirIn + '_side/' + file)
                
            

    print(file)

    
        
        
    

