# Normalize images 

import os
import numpy as np

dirIn = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped/041320/'


rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'annotate' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
rawfile_format = '%.0f,%9.2f,' + 2 * '%14.9f,' + '%9.2f,' + 9 * '%6.2f,' + 5 * '%7.2f,'+ '%d'
outfile_format = '%.0f,%d,' + 6 * '%3.2f,' + '%d,' + 3 * '%14.9f,' + 2 * '%5.2f,' + '%5.2f'



#### Start main code ##########################

os.chdir(dirIn)

date = dirIn.split('/')[-2]


for dir in os.listdir():
    if dir.find('.') >= 0:
        continue

    raw = np.genfromtxt(dir + '/raw_data.txt', delimiter=',', invalid_raise=False)
    out = np.genfromtxt(dir + '/out_data.txt', delimiter=',', invalid_raise=False)
    run_num = str(int(dir)).zfill(2)
    
#    for ix in range(len(raw)):
#        img_num = str(int(raw[ix, rawf['frame']])).zfill(5)
#        frameNew = int(date + run_num + img_num)
#        raw[ix, rawf['frame']] = frameNew
#        print('raw %s: %s -> %d' % (dir,img_num,frameNew))
#
    np.savetxt(dir + '/raw_data.txt', raw, fmt=rawfile_format, delimiter=',')
    
#    for ix in range(len(out)):
#        img_num = str(int(out[ix, outf['frame']])).zfill(5)
#        frameNew = int(date + run_num + img_num)
#        out[ix, outf['frame']] = frameNew
#        print('out %s: %s -> %d' % (dir,img_num,frameNew))

    #np.savetxt(dir + '/out_data.txt', out[:,0:15], fmt=outfile_format, delimiter=',')
    z=np.zeros((len(out),3))
    x=np.append(out[:,0:12],z,1)
    np.savetxt(dir + '/out_data.txt', x[:,0:15], fmt=outfile_format, delimiter=',')
