# process_LA_images.py -- rename image files to create unique file names and crop

#  process_LA_images dirIn 
#
#   dirIn example = C:\Drover\ImageFiles\LosAngeles\Raw\041420

import os, sys
import cv2
import numpy as np
import pandas as pd
import feather

raw = (640, 480)
#crop = (0,640,240,480) # crop to only use bottom half
crop = (0,640,160,480) # crop to only use bottom two thirds
resize = (224,224)

DATABASE = 'C:/Drover/ImageFiles/LosAngeles/LA_metadata.db'

dirOut = 'C:/Drover/ImageFiles/LosAngeles/Cropped/'

db_col = {'image':'int64', 'folder':'uint16', 'date':'int32', 'time':'uint32', 
          'lat':'float', 'lon':'float', 'hgt':'float',
          'velx':'int16', 'vely':'int16', 'velz':'int16', 
          'yaw':'int16', 'pitch':'int16', 'roll':'int16', 
          'accx':'int16', 'accy':'int16', 'accz':'int16',
          'gyrox':'int16', 'gyroy':'int16', 'gyroz':'int16',
          'odo':'int16', 'maxvel':'int16', 'annotate':'int8', 
          'label':'int8', 'bike_lane':'uint8', 'crosswalk':'uint8', 
          'sidewalk':'uint8', 'street':'uint8', 'man_label':'int8'}


MIN_VEL = 100 # rpm, ~2.5 mph

rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'annotate' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
rawfile_format = '%.0f,%9.2f,' + 2 * '%14.9f,' + '%9.2f,' + 9 * '%6.2f,' + 5 * '%7.2f,'+ '%d'
outfile_format = '%.0f,%d,' + 6 * '%3.2f,' + '%d,' + 3 * '%14.9f,' + 2 * '%5.2f,' + '%5.2f'

def process_img(img_in):
            img_out = cv2.resize(img_in[crop[2]:crop[3], crop[0]:crop[1]], resize,
                              interpolation = cv2.INTER_AREA)
            # adjust image mean if not done in scooter
            m = int(np.mean(img_out))
            img_out = np.uint8(np.clip(np.int16(img_out[:,:,:]) + 128 - m, 0, 255))
            return(img_out)
            
def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        pass            

########## Main code starts here ############################

# parse command line
if len(sys.argv)>1:
    path = sys.argv[1]
    dirIn = path + '/'
    path = path.split('/')
    dirOut = dirOut + path[-1] + '/'
else:
    print('Please include input folder on command line')

date = dirIn[-7:-1]
mkdir(dirOut)


# load database or create if it doesn't exist
if os.path.exists(DATABASE):
    df_all = pd.read_feather(DATABASE)    
else:
    df_all=[]

run_num = 0
for dir in os.listdir(dirIn): 
    if dir.find('.') >= 0: # check if dir is file
        continue
    
    dir_new = str(run_num)
    mkdir(dirOut + dir_new)
    file_prefix = date + '_' + str(run_num).zfill(2)
    
    # copy metadata to cropped folder
    #shutil.copy(dirIn + dir + '/raw_data.txt', dirOut + dir_new + '/raw_data.txt')
    #shutil.copy(dirIn + dir + '/out_data.txt', dirOut + dir_new + '/out_data.txt')


    # scale and adjust metadata for database  
    raw = np.genfromtxt(dirIn + dir + '/raw_data.txt', delimiter=',', invalid_raise=False)
    out = np.genfromtxt(dirIn + dir + '/out_data.txt', delimiter=',', invalid_raise=False)  
    raw_frames = raw[:, rawf['frame']]
    raw_odos = raw[:, rawf['odo']]  

    raw[:, rawf['imu']+2] = raw[:, rawf['imu']+2] - 90  # adjust roll
    raw[:,rawf['time']] *= 100   # scale
    raw[:,rawf['imu']:-3] *= 100   # scale 
    out[:,outf['class']:] *= 255 # scale
   
    # scale and adjust metadata for modified raw and out files
    raw0 = np.genfromtxt(dirIn + dir + '/raw_data.txt', delimiter=',', invalid_raise=False)
    out0 = np.genfromtxt(dirIn + dir + '/out_data.txt', delimiter=',', invalid_raise=False)
    raw0[:, rawf['imu']+2] = raw0[:, rawf['imu']+2] - 90  # adjust roll

    records=[]
    num_images = np.min((len(raw), len(out)))
    for ix in range(num_images):
        img_num = str(int(raw_frames[ix])).zfill(5)
        raw_frame = int(int(date) * 1e7 + run_num * 1e5 + int(img_num))
        
        #update image numbers in out and raw files
        raw0[ix, rawf['frame']] = raw_frame
        out0[ix, outf['frame']] = raw_frame
        
        # skip low velocity images
        if raw_odos[ix] < MIN_VEL:
                continue

        # create full record
        fileNew = date + '_' + str(run_num).zfill(2) + '_' + img_num + '.jpg'
        record = np.concatenate(([raw_frame], [run_num], [int(date)], 
                                 raw[ix, rawf['time']:], out[ix,1:6], [-1]))
        records.append(record)
        
        # crop and resize image and copy to cropped folder
        img_raw = cv2.imread(dirIn + dir + '/img_' + img_num + '.jpg')
        img = process_img(img_raw)
        cv2.imwrite(dirOut + dir_new + '/' + fileNew, img)

        print(img_num, fileNew)
   
    # update database with metadata
    df = pd.DataFrame(data=records, columns=db_col)
    # set types
    for k in db_col.items():
        df[k[0]]=df[k[0]].astype(k[1])
    if isinstance(df_all, pd.DataFrame):
        df_all = df_all.append(df, ignore_index=True)
    else:
        df_all = df
        
    # update raw and output files 
    np.savetxt(dirOut + dir_new + '/raw_data.txt', raw0[0:num_images,:], fmt=rawfile_format, delimiter=',')
    np.savetxt(dirOut + dir_new + '/out_data.txt', out0[0:num_images,0:15], fmt=outfile_format, delimiter=',')
    
    run_num += 1  
        
#write database back to disk
feather.write_dataframe(df_all,DATABASE)      
df_all.to_csv(DATABASE + '.csv', index=False)        
        
    
