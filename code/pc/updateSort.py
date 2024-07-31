# updateSort.py: update sort
#
import os, sys
import numpy as np

# Define class_results file formats 
sortf = {'frame' : 0, 'label' : 1}
 
# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}
classes = list(label_dict)
# Get input folder from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('No input folder specified on command line')
    
# load data files into arrays
try:
    sort = np.genfromtxt(dirIn + 'sort_results.txt', delimiter=',')
except:
    raise Exception('Unable to load data file')

# pull data from arrays
sort_frames = sort[:, sortf['frame']]
sort_labels = sort[:, sortf['label']]
num_frames = len(sort_frames)

# create list of files by class from sub-folders
os.chdir(dirIn)    
fileLists = []
for label in classes:
    fileLists.append(os.listdir(label))

 
# loop through images in each sub-folder and move to main folder
fileClass = 0
for fileList in fileLists:
    for file in fileList:
        if file[-4:] != '.jpg':
            continue
        image_num = float(file.replace('_','')[:-4])
        # first check if image is in sort file
        try:
            ix = np.where(sort_frames==image_num)[0][0]
        except:
            print('Image not found in sort file')
            continue
        # then check if current folder matches sort file folder
        if sort_labels[ix] != fileClass:
            #os.rename(file, file)
            print('Move file %s: %s -> %s' % (file, classes[fileClass], classes[int(sort_labels[ix])]))
            os.rename(classes[fileClass] + '/' + file,
                      classes[int(sort_labels[ix])] + '/' + file)
    fileClass +=1
        
 