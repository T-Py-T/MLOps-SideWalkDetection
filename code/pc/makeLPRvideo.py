# makeLPRvideo.py --  Combine images from scooter with LPR data
#                         to create video
import os
import cv2, sys
import numpy as np
import time
import pandas as pd

low_conf_thresh = 40
hi_conf_thresh = 60


print("\n\nPress 'q' to quit, or <space> to pause/continue\n\n")

# Check command line arguments
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
else:
    raise Exception('Input Folder Missing')
    
    
# load files into arrays
#try:
my_cols = ['c' + str(i) for i in range(34)]
lpr = pd.read_csv(dirIn + '/lpr_data.txt', sep=',|:', 
                  names = my_cols)
num_img = len(lpr.c1)

img_nums = lpr.c3
plates = lpr.c9
conf = np.zeros(num_img)
box0 = np.zeros(num_img)
box7 = np.zeros(num_img)
for i in range(num_img):
    if lpr.c6[i] != None:
        conf[i] = float(lpr.c6[i][1:])
        box0[i] = float(lpr.c11[i][1:])
        box7[i] = float(lpr.c18[i][:-4])
box = np.vstack(([box0, lpr.c12], [lpr.c13, lpr.c14],
                 [lpr.c15, lpr.c16], [lpr.c17, box7]))

box = np.transpose(box)


# Define the codec and create VideoWriter object for output video
videoFileOut=dirIn + '/' + os.path.basename(dirIn) + '.mp4'
fps=4.0;
(w,h) = (int(1648/2), int(632/2))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
videoOut = cv2.VideoWriter(videoFileOut,fourcc, fps, (w,h))
font = cv2.FONT_HERSHEY_SIMPLEX

# get list of images in input folder
fnames = sorted([fname for fname in os.listdir(dirIn)])

# loop through images
for file in fnames:
    print(file)
    if file[-4:] != '.jpg':
        continue
    frame=cv2.imread(dirIn + '/' + file)
 
    # find image data in output file
    img_num = int(file[-9:-4])
    #img_num = int(file[-13:-9])
    try:
        ix = np.where(img_nums == img_num)[0][0]
    except:
        ix = 0
        box[ix][0] = 0
    
    pts = box[ix]
    if pts[0] != 0 and conf[ix] > low_conf_thresh:
        pts = np.array([[pts[0],pts[1]],[pts[2],pts[3]],
                        [pts[4],pts[5]],[pts[6],pts[7]]], np.int32)
        pts = pts.reshape((-1,1,2))
        
        
        # add box with plate number
        labelSize=cv2.getTextSize(plates[ix][1:-1],font,1.0,2)
        r1 = (pts[3][0][0], pts[3][0][1])
        r2 = (pts[3][0][0] + labelSize[0][0], pts[2][0][1] + labelSize[0][1]*2)
        if conf[ix] > hi_conf_thresh:
            cv2.polylines(frame, [pts], True, (0,255,0), thickness=2)
            cv2.rectangle(frame,r1,r2,(0,255,0),cv2.FILLED)
        elif conf[ix] > low_conf_thresh:
            cv2.polylines(frame, [pts], True, (0,255,255), thickness=2)
            cv2.rectangle(frame,r1,r2,(0,255,255),cv2.FILLED)
    
    
        # add plate number to image  
        cv2.putText(frame, plates[ix][1:-1], 
                    (pts[3][0][0],pts[3][0][1]+30), font, 1.0, (0,0,0), 2, cv2.LINE_AA)
        print('Plate: %s Conf: %.1f' % (plates[ix][1:-1], conf[ix]))


    # add frame number to image  
    cv2.putText(frame, 'FRAME = ' + str(img_num), 
                (w-140,40), font, 0.5, (0,0,0), 2, cv2.LINE_AA)
    
    # resize and display frame
    frame = cv2.resize(frame, (w,h), interpolation = cv2.INTER_AREA)
    cv2.imshow('frame',frame)


    # write image to video
    videoOut.write(frame)
    if box[ix][0] != 0:
        for i in range(1): 
            videoOut.write(frame)

    time.sleep(0.02)

    # check for user pause or quit
    key=cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # quit
        break 
    elif key == ord(' '):  #pause
        cv2.waitKey(0)
        
    if box[ix][0] != 0 and conf[ix] > low_conf_thresh:
        time.sleep(1.5)



videoOut.release()
cv2.destroyAllWindows()