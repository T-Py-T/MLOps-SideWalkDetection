import cv2
import os

dirIn = 'D:/consulting/Pathwise/hollywood/hw_test1/'
dirOut = 'D:/consulting/Pathwise/hollywood/hw_test1_crop2/'

#crop = (0,640,0,480) # no crop
crop = (0,640,240,480) # crop bottom half
resize = (224,224)

try:
    os.mkdir(dirOut)
except:
    pass


def cropImages(dirIn,dirOut):
    for file in os.listdir(dirIn):
            if file[-4:] != '.jpg':
                print('Bad file: %s' % file)
                continue
        #try:
            print(file)
            image1 = cv2.imread(os.path.join(dirIn,file))
            image2 = image1[crop[2]:crop[3], crop[0]:crop[1]]
            image3 = cv2.resize(image2, resize, interpolation = cv2.INTER_AREA)
            cv2.imwrite(os.path.join(dirOut,file),image3)
            
        #except:
            pass

#  Crop set of folders
for dir in os.listdir(dirIn):
    
    try:
        os.mkdir(dirOut + dir)
    except:
        pass
    cropImages(dirIn + dir, dirOut + dir)


# Crop single folder
#cropImages(dirIn, dirOut)



