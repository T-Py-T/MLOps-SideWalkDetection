# resortImages.py -- Use to resort images afeter doing an unsort
#
# sortLabeledImages.py inputFolder
#
# Uses the results saved when unsortImages.py was run and the results put into
# the sort_results.txt file

import os
import sys
import numpy as np

# Define class_results file formats 
sortf = {'frame' : 0, 'label' : 1}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3, 'unknown' : 4}


# Get input folder from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('Input Folder Missing')
    
    
# create sub-folders with class labels
try:
    for label in list(label_dict):
        os.mkdir(dirIn + label)
except:
    pass
    
# load data files into arrays
try:
    sort = np.genfromtxt(dirIn + 'sort_results.txt', delimiter=',')
except:
    raise Exception('Unable to load data file')

# pull data from arrays
img_nums = sort[:, sortf['frame']]
classes = sort[:, sortf['label']]
num_images = len(img_nums)

# get list of images in input folder    
fnames = sorted([fname for fname in os.listdir(dirIn)])

# loop through images and move to sub-folders
for file in fnames:
    try:
        img_num = int(file[-19:-13] + file[-12:-10] + file[-9:-4]) # get image number from file name 
        ix=np.where(img_nums==img_num)[0][0] # find image in summary file
        os.rename(dirIn + file, dirIn + list(label_dict)[int(classes[ix])] + '/' + file)
        print(file)
    except:
        print('Err: %s' % file)
        continue
    