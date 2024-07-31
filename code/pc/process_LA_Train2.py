# process_LA_train2 image set


import os, shutil
import numpy as np
import pandas as pd
import feather


dirIn = 'D:/consulting/Pathwise/LosAngeles/LA_train2/train/'
dirOut = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped/'

DATABASE = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/LA_metadata.db'
db_col = {'image':'int64', 'folder':'uint16', 'date':'int32', 'time':'uint32', 
          'lat':'float', 'lon':'float', 'hgt':'float',
          'velx':'int16', 'vely':'int16', 'velz':'int16', 
          'yaw':'int16', 'pitch':'int16', 'roll':'int16', 
          'accx':'int16', 'accy':'int16', 'accz':'int16',
          'gyrox':'int16', 'gyroy':'int16', 'gyroz':'int16',
          'odo':'int16', 'maxvel':'int16', 'annotate':'int8', 
          'label':'int8', 'bike_lane':'uint8', 'crosswalk':'uint8', 
          'sidewalk':'uint8', 'street':'uint8', 'man_label':'int8'}


rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'annotate' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
sortf = {'frame' : 0, 'label' : 1}

            
def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        pass            

########## Main code starts here ############################




# load database or create if it doesn't exist
if os.path.exists(DATABASE):
    df_all = pd.read_feather(DATABASE)    
else:
    df_all=[]

sort = np.genfromtxt(dirIn + 'sort_results.txt', delimiter=',')
sort_frames = sort[:,sortf['frame']]
sort_labels = sort[:,sortf['label']]

run_num = 0
for file in os.listdir(dirIn): 
    if 'raw_data' not in file: # skip other files
        continue

    # get metadata    
    raw = np.genfromtxt(dirIn + file, delimiter=',')
    raw_frames = raw[:, rawf['frame']]
    id = str(int(raw_frames[0])).zfill(13)
    date = id[:6]
    run_num = int(id[6:8])
    
    mkdir(dirOut + date)
    mkdir(dirOut + date + '/' + str(run_num))
        
    # scale and adjust metadata
    raw[:, rawf['imu']+2] = raw[:, rawf['imu']+2] - 90  # adjust roll
    raw[:,rawf['time']] *= 100   # scale 
    raw[:,rawf['imu']:-3] *= 100   # scale 
    
    # adjust annotate switch
    raw[:,rawf['annotate']] *= 0  
    raw[:,rawf['annotate']] -= 1


    records=[]
    for ix in range(len(raw)):
        id = str(int(raw_frames[ix])).zfill(13)
        # find file in sort results, skip if not there
        try:
            ix_sort = np.where(sort_frames == int(id))[0][0]
        except:
            print('Image not found in sort results: %s' % id)
            continue
        labels =[sort_labels[ix_sort],0,0,0,0]
        man_label = [sort_labels[ix_sort]]
        record = np.concatenate(([raw_frames[ix]], [run_num], [int(date)], 
                                 raw[ix, rawf['time']:], labels, man_label))
        records.append(record)
        # copy image to cropped folder
        fileNew = id[0:6] + '_' + id[6:8] + '_' + id[8:] + '.jpg'
        #shutil.copy(dirIn + fileNew, dirOut + date + '/' + str(run_num) + '/' + fileNew)
        print(id)
            
    # copy metadata to cropped folder
    shutil.copy(dirIn + file, dirOut + date + '/' + str(run_num) + '/raw_data.txt')

    
    # update database with metadata
    df = pd.DataFrame(data=records, columns=db_col)
    # set types
    for k in db_col.items():
        df[k[0]]=df[k[0]].astype(k[1])
        
    if isinstance(df_all, pd.DataFrame):
        df_all = df_all.append(df, ignore_index=True)
    else:
        df_all = df

    
    run_num += 1  
        
#write database back to disk
feather.write_dataframe(df_all,DATABASE)      
df_all.to_csv(DATABASE + '.csv', index=False)        
        
    
