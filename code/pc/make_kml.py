import simplekml
import numpy as np
import sys, os

kml = simplekml.Kml()

dirIn = sys.argv[1]
os.chdir(dirIn)

# Define raw data and output file formats 
rawf = {'frame' : 0,	'time' : 1, 'gps' : 2, 'imu' : 8, 'odo' : 17, 'annotate' : 19}
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}

# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}
labels = list(label_dict)

raw=[]

for fname in os.listdir():
    if 'raw_data' in fname:
        r = np.genfromtxt(fname, delimiter=',')
        if len(raw) == 0:
            raw = r
        else:
            raw = np.concatenate((raw, r))
    elif 'out_data' in fname:
        out = np.genfromtxt(fname, delimiter=',')
    else:
        pass

raw_frames = raw[:,rawf['frame']]
raw_llhs = raw[:,rawf['gps']:rawf['gps']+2]
out_frames = out[:,outf['frame']]
out_labels = out[:,outf['label']]


style_st = simplekml.Style()
style_sw = simplekml.Style()
style_cw = simplekml.Style()
style_bk = simplekml.Style()

style_st.labelstyle.scale = 0.0  # Make the text twice as big
style_st.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml//paddle/grn-circle-lv.png'
style_st.iconstyle.scale = 0.2  # Make the text twice as big

style_sw.labelstyle.scale = 0.0  # Make the text twice as big
style_sw.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml//paddle/red-circle-lv.png'
style_sw.iconstyle.scale = 0.2  # Make the text twice as big

style_cw.labelstyle.scale = 0.0  # Make the text twice as big
style_cw.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml//paddle/ylw-circle-lv.png'
style_cw.iconstyle.scale = 0.2  # Make the text twice as big

style_bk.labelstyle.scale = 0.0  # Make the text twice as big
style_bk.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml//paddle/blu-circle-lv.png'
style_bk.iconstyle.scale = 0.2  # Make the text twice as big

cnt = 0
for raw_frame, raw_llh in zip(raw_frames, raw_llhs):
    if raw_llh[0] == 0.0:
        continue
    try:
        ix = np.where(out_frames==raw_frame)[0][0]
    except:
        continue
    
    cnt += 1
    if cnt // 1 != cnt / 1:
        continue

    pnt = kml.newpoint(name='P')
    pnt.coords = [(raw_llh[1], raw_llh[0])]
    

    if out_labels[ix] == label_dict['crosswalk']:
        pnt.style = style_cw
    elif out_labels[ix] == label_dict['bike_lane']:
        pnt.style = style_bk
    elif out_labels[ix] == label_dict['side']:
        pnt.style = style_sw
    elif out_labels[ix] == label_dict['street']:
        pnt.style = style_st
        



kml.save(os.path.basename(dirIn) + '.kml')