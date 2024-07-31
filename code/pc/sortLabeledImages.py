# sortLabeledImages -- Sort images downloaded from scooter by classifier and 
#                      joystick labelling results
#
# sortLabeledImages.py inputFolder [sort] [thresh]
#
#   sort = 'joy':    sort priority is joystick position, then classifier [default]
#   sort = 'class':  sort priority is classifier output, then joystick 
#   sort = 'score':  sort priority is classifier scores above threshold
#   sort = 'odo':    sort priority is odometer velocity, use thresh if odo>10
#   sort = 'last':   sort priority is classfier output, low qual if doesn't match previous 
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
# Define class_results file formats 
resf = {'frame' : 0, 'label' : 1}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'back' : 0, 'intersect' : 1, 'side' : 2, 'street' : 3}

# define joystick choices
joy_intersect = 0
joy_sw = 1
joy_street = 2


# Get input parameters from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('Input Folder Missing')
    
if len(sys.argv) > 2:
    sortType = sys.argv[2]
else:
    sortType = 'joy'
    
if len(sys.argv) > 3:
    try:   # if number, then is threshold
        score_thresh = float(sys.argv[3])
    except:   # else is default class
        def_class = sys.argv[3]

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
if not os.path.exists(dirIn + '_unknown'):
        os.mkdir(dirIn + '_unknown')


    
# load data files into arrays
if os.path.exists(dirIn + 'out_data.txt'):
    out = np.genfromtxt(dirIn + 'out_data.txt', delimiter=',')
else:
    raise Exception('Unable to load data file')
if os.path.exists(dirIn + 'raw_data.txt'):
    try:
        raw = np.genfromtxt(dirIn + 'raw_data.txt', delimiter=',')
    except:
        print('\n Unable to read raw data fil \n')
        #raise
else:
    raw = np.zeros((len(out),rawf['joy']+1))

# pull data from arrays
img_nums = out[:, outf['frame']]
num_images = len(img_nums)

scores = np.zeros((num_images, num_classes))
for n in range(num_classes):
    scores[:, n] = out[:, outf['class'] + n]
    
joy_inputs = raw[:, rawf['joy']]
odo = raw[:, rawf['odo']]
max_ix = min(len(img_nums), len(joy_inputs)) - 1

# get list of images in input folder    
fnames = sorted([fname for fname in os.listdir(dirIn)])

# load previous results if needed
if sortType == 'last':
    try:
        res = np.genfromtxt(dirIn + 'sort_results.txt', delimiter=',')
    except:
        raise Exception('Unable to load previous sort results')
    lastSort = res[:, resf['label']]

# loop through images
for file in fnames:

    if file[-4:] != '.jpg':
        continue
    
    try:
        #img_num = int(file[-9:-4])  # get image number from file name 
        img_num = int(file[-19:-13] + file[-12:-10] + file[-9:-4])
        ix = np.where(img_nums==img_num)[0][0] # find image in summary file
    except:
        print(file,img_num)
        continue

    if sortType == 'joy':
        # if classifier and switch label agree, put directly in final folders,
        # otherwise put in temp folders using joystick value
        if ix > max_ix:
            os.rename(dirIn + file, dirIn + '_unknown/' + file)
            
        elif joy_inputs[ix] == joy_street:
            if scores[ix, label_dict['street']] > score_thresh:
                os.rename(dirIn + file, dirIn + 'street/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_street/' + file)
                
        elif joy_inputs[ix] == joy_intersect:
            if scores[ix, label_dict['intersect']] > score_thresh:
                os.rename(dirIn + file, dirIn + 'intersect/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_intersect/' + file)
                
        elif int(joy_inputs[ix]) & joy_sw == joy_sw:
            if scores[ix, label_dict['side']] > score_thresh:
                os.rename(dirIn + file, dirIn + 'side/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_side/' + file)
                
        else:
            os.rename(dirIn + file, dirIn + '_unknown/' + file)
            
    elif sortType == 'class':
        # if classifier and switch label agree, put directly in final folders,
        # otherwise put in temp folders using classifier value
        if ix > max_ix:
            os.rename(dirIn + file, dirIn + '_unknown/' + file)
                
        elif scores[ix, label_dict['intersect']] > score_thresh:
            if joy_inputs[ix] == joy_intersect:
                os.rename(dirIn + file, dirIn + 'intersect/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_intersect/' + file)
            
        elif scores[ix, label_dict['street']] > score_thresh:
            if joy_inputs[ix] == joy_street:
                os.rename(dirIn + file, dirIn + 'street/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_street/' + file)
                
        elif scores[ix, label_dict['side']] > score_thresh:
            if int(joy_inputs[ix]) & joy_sw == joy_sw:
                os.rename(dirIn + file, dirIn + 'side/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_side/' + file)

        else:
            os.rename(dirIn + file, dirIn + '_unknown/' + file)
            
    elif sortType == 'score':
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
                
    elif sortType == 'odo':
        if  odo[ix] < 10.0:
            os.rename(dirIn + file, dirIn + 'intersect/' + file)
        else:
            os.rename(dirIn + file, dirIn + def_class + '/' + file)  
    
    elif sortType == 'last':
        ix_sort = np.where(img_nums == img_num)[0][0]
        if scores[ix,:].argmax() == label_dict['intersect']:
            if lastSort[ix_sort] == label_dict['intersect']:
                os.rename(dirIn + file, dirIn + 'intersect/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_intersect/' + file)
                
        if scores[ix,:].argmax() == label_dict['street']:
            if lastSort[ix_sort] == label_dict['street']:
                os.rename(dirIn + file, dirIn + 'street/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_street/' + file)
                
        if scores[ix,:].argmax() == label_dict['side']:
            if lastSort[ix_sort] == label_dict['side']:
                os.rename(dirIn + file, dirIn + 'side/' + file)
            else:
                os.rename(dirIn + file, dirIn + '_side/' + file)
        
    else:
       raise Exception('Invalid sort option') 
 
    print(file)

    
        
        
    

