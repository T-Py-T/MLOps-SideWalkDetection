# sortImages -- Sort images downloaded from scooter by classifier and 
#                      annotation switch results
#
# sortLabeledImages.py inputFolder [sort] [thresh]
#
#   sort = 'switch': sort priority is annotation switch position, then classifier 
#   sort = 'class':  sort priority is classifier output, then annotation switch 
#   sort = 'score':  sort priority is classifier scores above threshold (default)
#   sort = 'last':   high confidence if label matches previous label 
#
#   thresh:  threshold for high confidence classifer score
#
# Images will be moved to sub-folders inside the input folder.  Sub-folder names
# without leading underscores contain images with agreement between annotation switch
# label and classifier.  Leading underscore in the sub-folder name indicates 
# the two classifications did not agree or classifier score was below threshold.
# These should be manually sorted

import os
import sys
import numpy as np

# Define raw data and output file formats 
rawf = {'frame' : 0, 'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'switch' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
# Define sort_results file formats 
sortf = {'frame' : 0, 'label' : 1}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3, 'unknown' : 4}

# define annotation switch decode, switch value : class
switch_dict = {0 : -1, 1 : 2, 2 : 3, 3 : -3, 4 : -2, 5 : 1, 6 : 0, 7: -3}

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
    sortType = 'score'
    
subFolders = False
if len(sys.argv) > 3:
    try:   # if number, then is threshold
        score_thresh = float(sys.argv[3])
    except:   # else is default class
        subFolders = (sys.argv[3] == '-r')


else:
    score_thresh = 0.8
    
 # get class labels from dictionary
labels = list(label_dict)
num_classes = len(labels)

# get list of sub-folders
os.chdir(dirIn)
if subFolders:
    dirs = []
    d=os.listdir('.')
    for f in d:
        if os.path.isdir(f):
            dirs.append(f)
else:
    dirs = ['.']       

for dir in dirs:  
    dir = dir + '/'
    # create sub-folders with class labels
    for label in labels:
        if not os.path.exists(dir + label):
            os.mkdir(dir + label)  # folder for high confidence images
        if not os.path.exists(dir + '_' + label):
            os.mkdir(dir + '_' + label)  # temp folder for low confidence images
    
        
    # load data files into arrays
    if os.path.exists(dir + 'out_data.txt'):
        out = np.genfromtxt(dir + 'out_data.txt', delimiter=',')
    else:
        raise Exception('Unable to load out file')
    if os.path.exists(dir + 'raw_data.txt'):
        raw = np.genfromtxt(dir + 'raw_data.txt', delimiter=',')
    else:
        raise Exception('\n Unable to read raw file \n')
            
    # load previous results if needed
    if sortType == 'last':
        try:
            sort = np.genfromtxt(dir + 'sort_results.txt', delimiter=',', dtype=np.int64)
        except:
            raise Exception('Unable to load previous sort results')
    
    # pull data from arrays
    out_img_nums = out[:, outf['frame']]
    out_num_images = len(out_img_nums)
    dir_num = out_img_nums[0] // 100000 * 100000
    out_scores = np.zeros((out_num_images, num_classes))
    for n in range(num_classes):
        out_scores[:, n] = out[:, outf['class'] + n]
        
    if sortType == 'last':
        sort_img_nums = sort[:, sortf['frame']]
        sort_labels = sort[:, sortf['label']]
        max_ix = len(sort_img_nums)
    else:
        raw_img_nums = raw[:, rawf['frame']]
        raw_switch_inputs = raw[:, rawf['switch']]
        max_ix = min(len(out_img_nums), len(raw_switch_inputs)) - 1
    # get list of images in input folder    
    fnames = sorted([fname for fname in os.listdir(dir)])
    
    # loop through images
    for file in fnames:
        if file[-4:] != '.jpg':
            print('Err:%s' % file)
            continue
        
        try:
            img_num = int(file[-19:-13] + file[-12:-10] + file[-9:-4])  
            #img_num = int(file[-9:-4]) 
            out_ix = np.where(out_img_nums==img_num)[0][0] # find image in summary file
        except:
            print('Entry not found: %s' % file)
            continue
    
        
        # find highest class score
        max_class_ix = out_scores[out_ix,:].argmax()
        
        if sortType == 'last':
            sort_ix = np.where(sort_img_nums==img_num)[0][0] # find image in summary file
        else:
            try:
                raw_ix = np.where(raw_img_nums==img_num)[0][0] # find image in summary file
            except:
                print('Raw Err: %s' % file)
                continue
            switch_ix = switch_dict[raw_switch_inputs[raw_ix]]
            if switch_ix == -1:  # mixed, ok
                switch_ix = max_class_ix   # use inference result
        
        if out_ix > max_ix:
            os.rename(dir + file, dir + '_unknown/' + file)
    
        elif sortType == 'switch':
            # if classifier and switch label agree, put directly in final folders,
            # otherwise put in temp folders using joystick value
            if out_scores[out_ix, switch_ix] > score_thresh:
                os.rename(dir + file, dir + labels[switch_ix] + '/' + file)
            else:
                os.rename(dir + file, dir + '_' + labels[switch_ix] + '/' + file)
                
        elif sortType == 'class':
            # if classifier and switch label agree, put directly in final folders,
            # otherwise put in temp folders using classifier value
            if switch_ix == max_class_ix:
                os.rename(dir + file, dir + labels[switch_ix] + '/' + file)
            else:
                os.rename(dir + file, dir + '_' + labels[switch_ix] + '/' + file)        
         
        elif sortType == 'score':
            # if max classifier score is above threshold, put directly in final
            # folders, else put in temp folders
            if out_scores[out_ix, max_class_ix] > score_thresh:
                os.rename(dir + file, dir + labels[max_class_ix] + '/' + file)
            else:
                os.rename(dir + file, dir + '_' + labels[max_class_ix] + '/' + file)            
    
        elif sortType == 'last':
            # if max classifier score matches last sor, put directly in final
            # folders, else put in temp folders
            if max_class_ix == sort_labels[sort_ix]:
                os.rename(dir + file, dir + labels[max_class_ix] + '/' + file)
                #print('match')
            else:
                os.rename(dir + file, dir + '_' + labels[sort_labels[sort_ix]] + '/' + file) 
                #print('no match')
           
        else:
           raise Exception('Invalid sort option') 
     
        print(file)

    
        
        
    

