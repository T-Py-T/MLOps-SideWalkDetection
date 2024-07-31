# add images from data run to training data set

import numpy as np
import shutil
import sys, os

dirIn = sys.argv[1]
dirDB = 'J:/consulting/pathwise/denver_db/'

# Define raw data and output file formats 
rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'joy' : 18}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}


db_street = os.listdir(dirDB + 'street')
db_side = os.listdir(dirDB + 'side')
db_intersect = os.listdir(dirDB + 'intersect' )

in_street = os.listdir(dirIn + '/street')
in_side = os.listdir(dirIn + '/side')
in_intersect = os.listdir(dirIn + '/intersect' )


if os.path.exists(dirIn + '/raw_data.txt'):    
    raw = np.genfromtxt(dirIn + '/raw_data.txt', delimiter=',')
    out = np.genfromtxt(dirIn + '/out_data.txt', delimiter=',')
else:
    print('Raw data file not found')
    raise

frames = out[:, outf['frame']]
lats = raw[:, rawf['gps'] + 1]
lons = raw[:, rawf['gps']]
swflags = out[:, outf['swFlag']]

# convert lat, lon to east, north
easts = lons2easts(lons)
norths = lat2norths(lats)

for frame,north,east,swflag in frames,norths,easts,swflags:
    # create file name from location
    fname = str(north) + str(east)
    fdir = str(swflags)
    # check if file exists in dir
    if fname not in fdir:
        # rename and copy file and add it to training data
        shutil.copy(from,to)
    
    