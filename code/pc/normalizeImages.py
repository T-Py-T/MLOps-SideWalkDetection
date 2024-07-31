# Normalize images 

import cv2
import os
import numpy as np

#dirIn = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped/041320/'
#dirOut = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped/041320/'
dirIn = 'D:/consulting/Pathwise/alpha2/run4'
dirOut = 'D:/consulting/Pathwise/alpha2/run4a/'


def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        pass  


def normImages(dirIn, dirOut):
    for file in os.listdir(dirIn):
        if file[-4:] != '.jpg':
            print('Invalid file: %s' % file)
            continue
        img = cv2.imread(os.path.join(dirIn,file))
        img2 = img.copy()
        m = []
        for i in range(3):
            m.append(int(np.mean(img[:,:,i])))
            img2[:,:,i] = np.uint8(np.clip(np.int16(img2[:,:,i]) + 128 - m[i], 0, 255))
        cv2.imwrite(os.path.join(dirOut,file),img2)
        print('%s: %s' % (file, m))


#### Start main code ##########################

mkdir(dirOut)
os.chdir(dirIn)

#  Normalize set of folders
for dir in os.listdir():
    if dir.find('.') >= 0:
        continue
    mkdir(dirOut + dir)
    print(dirOut)
    normImages(dir, dirOut + dir)




