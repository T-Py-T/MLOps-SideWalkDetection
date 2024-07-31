# compareOutFiles.py: compare two out files
#
#   compareOut.py inputFolder <-nosort>
#
#    -nosort: create sort file but don't move images
#
import os, sys
import numpy as np

def mkdir(dir):
    try:
        os.mkdir(dir)
    except:
        pass

########### start main code

# Define output file format 
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}


# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3}
classes = list(label_dict)
num_classes = len(classes)

# Get input folders from command line
if len(sys.argv) > 1:
    os.chdir(sys.argv[1])
else:
    raise Exception('No input folder specified on command line')
    
nosort = 0
if len(sys.argv) > 2:
    if sys.argv[2] == '-nosort':
        nosort = 1
    
# load data files into arrays
for fname in os.listdir():
    if fname == 'out_data.txt':
        out1 = np.genfromtxt(fname, delimiter=',')
    elif 'out_data.txt' in fname:
        out2 = np.genfromtxt(fname, delimiter=',')

# pull data from arrays
frames1 = out1[:, outf['frame']]
labels1 = out1[:, outf['label']]
scores1 = np.zeros((len(frames1), num_classes))
for n in range(num_classes):
    scores1[:, n] = out1[:, outf['class'] + n]
frames2 = out2[:, outf['frame']]
labels2 = out2[:, outf['label']]
scores2 = np.zeros((len(frames2), num_classes))
for n in range(num_classes):
    scores2[:, n] = out2[:, outf['class'] + n]

# loop through out1 and compare to out2
for frame1, label1 in zip(frames1, labels1):
    try:
        ix = np.where(frames2==frame1)[0][0]
    except:
        print('File not found in out2: %s' % frame1)
        continue
    label2 = labels2[ix]
    if label1 != label2:
        # move image to new folder
        destDir = label1 + '_' + label2
        f = frame1
        file = f[:-7] + '_' + f[-7:-5] + '_' + f[-5:] + '.jpg'
        mkdir(destDir)
        try:
            if nosort == 0:
                os.rename(label1 + '/' + file, destDir + '/' + file)
            print('%s: %s -> %s' % (file, label1, destDir))
        except:
            print('File not found: %s' % file)
        
        
 