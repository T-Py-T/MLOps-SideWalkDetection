# create training and validation folders

import os
from distutils.dir_util import copy_tree

rootDir = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped'
image_dirs = ['040120', '040220', '040320', '040520']
outDir = 'LA_train2'
classes = ['bike_lane', 'crosswalk', 'side', 'street']

def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        pass

############# main code #################

os.chdir(rootDir)
trainDir = rootDir + '/' + outDir + '/train'
valDir = rootDir + '/' + outDir + '/val'
mkdir(rootDir + '/' + outDir)
mkdir(trainDir)
mkdir(valDir)
for c in classes:
    mkdir(trainDir + '/' + c)
    mkdir(valDir + '/' + c)

for dateDir in image_dirs:
    for rideDir in os.listdir(dateDir):
        if rideDir == 'mixed':
            destDir = valDir
        else:
            destDir = trainDir
            
        for classDir in os.listdir(dateDir + '/' + rideDir):
            dir = dateDir + '/' + rideDir + '/' + classDir
            if classDir in classes:
                print('Copy: %s -> %s' % ( dir,destDir[-5:] + '/' + classDir))
                copy_tree(dir, destDir + '/' + classDir )
            else:
                #print('Skip: %s -> %s' % ( dir,destDir[-5:]))
                pass
