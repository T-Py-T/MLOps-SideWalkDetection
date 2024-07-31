import os
import glob

folders=('side/','street/','intersect/')
labelsIn='j:/tensorflow/images/denver6a/'
imagesIn='j:/tensorflow/images/denver_logi/'
# names reversed below to cancel mistake in creating folders
imageFNames=('ride2','ride2a','ride3','side1','side2','street1','street2')
labelFNames=('ride2_0425','ride2a_0415','ride3_0425','street1_0514','street2_0514','sidewalk1_0514','sidewalk2_0514')




for imageFName,labelFName in zip(imageFNames, labelFNames):
    for folder in folders:
        #filesIn = os.listdir(labelsIn + folder + '/'+ labelFName)
        filesIn = glob.glob(labelsIn + folder + '/'+ labelFName + '*')
    
        for fileIn in filesIn:
            if fileIn[-4:] == '.jpg':
                fileOut = imageFName + fileIn[-9:]
                try:
                    os.rename(imagesIn + fileOut, imagesIn + folder + fileOut)
                    print(fileOut)
                except:  # indicates duplicate image number
                    print('Err: %s\n' % fileOut)

        
        
    

