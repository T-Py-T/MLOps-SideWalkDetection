import sys
import numpy as np
from matplotlib import pyplot as plt


odo_scale = 15/600

# Define raw data and output file formats 
rawf = {'frame' : 0, 'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'joy' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}
# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}

# Check command line arguments
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
else:
    raise Exception('Input Folder Missing')
    
out = np.genfromtxt(dirIn + '/out_data.txt', delimiter=',')
raw = np.genfromtxt(dirIn + '/raw_data.txt', delimiter=',')

# pull data from arrays
secs = raw[:, rawf['time']]
sw_flag = out[:,outf['swFlag']]
speed = raw[:,rawf['odo']] * odo_scale
max_speed = raw[:,rawf['odo'] + 1] * odo_scale
gps_vx = raw[:,rawf['gps']+3]
gps_vy = raw[:,rawf['gps']+4]
gps_v = np.sqrt(gps_vx**2 + gps_vy**2)

plt.plot(secs, speed, secs, max_speed, secs, 10-sw_flag*5)
plt.grid()
plt.show()