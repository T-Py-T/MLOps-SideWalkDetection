# post_annotate.py

# post_annotate.py dirIn

# - Use sort_results.txt to add annotation switch values to raw_out.txt 

import os, sys
import numpy as np

# Define file formats 
rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'annotate' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
rawfile_format = '%.0f,%9.2f,' + 2 * '%14.9f,' + '%9.2f,' + 14 * '%5.2f,' + '%d'

# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}
Labels = list(label_dict)

# parse command line
if len(sys.argv)>1:
    path = sys.argv[1]
    dirIn = path + '/'
else:
    print('Please include input folder on command line')
    
dirs = os.listdir(dirIn)

for dir in dirs:
    print(dir)

    if dir == 'bike' or dir == 'street':
        blink = 2
    elif dir == 'side':
        blink = 1
    elif dir == 'mixed':
        blink = 3
    else:
        raise Exception('Invalid folder name')
        
    dir = dirIn + dir + '/'

    # load data files into arrays
    if os.path.exists(dir + 'out_data.txt'):
        out = np.genfromtxt(dir + 'out_data.txt', delimiter=',')
    else:
        raise Exception('Unable to load out file')
    os.rename(dir + 'raw_data.txt', dir + 'raw0_data.txt')
    if os.path.exists(dir + 'raw0_data.txt'): 
        raw = np.genfromtxt(dir + 'raw0_data.txt', delimiter=',')

    else:
        raise Exception('Unable to load raw file')
        
    # pull data from arrays
    out_frames = out[:, outf['frame']]
    out_labels = out[:, outf['label']]
    raw_frames = raw[:, rawf['frame']]
    raw_annotates = raw[:, rawf['annotate']]
    
    num_raw_images = len(raw_frames)
    for ix in range(num_raw_images):
        raw_annotates[ix] = blink + 4  # no modifier (button not pressed)
        raw_frames[ix] += int(out_frames[0]//10000 * 10000)
    
    for out_frame, out_label in zip(out_frames, out_labels):
        try:
            ix = np.where(raw_frames == out_frame)[0][0]
        except:
            continue
        print(ix)
        
        if blink == 2 and out_label != label_dict['bike_lane']:
                raw_annotates[ix] -= 4  # street
        elif blink == 1 and out_label != label_dict['crosswalk']: 
                raw_annotates[ix] -= 4  # sidewalk
           
        
    # save modified raw file
    raw[:, rawf['annotate']] = raw_annotates
    raw[:, rawf['frame']] = raw_frames
    np.savetxt(dir + '/raw_data.txt', raw, fmt=rawfile_format, delimiter=',')

