import cv2

videoFile = "D:/consulting/Pathwise/lpr/IMG_0846.mov"
dirOut = "D:/consulting/Pathwise/lpr/IMG_0846_full/"


vidcap = cv2.VideoCapture(videoFile)
success,image = vidcap.read()
h,w,c=image.shape

frameId = 0
while success:
    success, image = vidcap.read()
    if success:
        #image=image[0:h, 300:900]
        print(frameId)
        cv2.imwrite("{0:s}image_{1:04d}_full.jpg".format(dirOut,frameId), image)
        frameId +=1
        
vidcap.release()
print("Complete")