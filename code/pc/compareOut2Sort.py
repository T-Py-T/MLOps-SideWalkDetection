# compareOut2Sort.py: compare out file to sort file
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
    
# load data files into arrays
for fname in os.listdir():
    if fname == 'sort_results.txt':
        sort = np.genfromtxt(fname, delimiter=',')
    elif 'out_data.txt' in fname:
        out = np.genfromtxt(fname, delimiter=',')

# pull data from arrays
frames1 = sort[:, outf['frame']]
labels1 = sort[:, outf['label']]
frames2 = out[:, outf['frame']]
labels2 = out[:, outf['label']]
scores2 = np.zeros((len(frames2), num_classes))
for n in range(num_classes):
    scores2[:, n] = out[:, outf['class'] + n]

# loop through sort file and compare to out file
n_move = 0
for frame1, label1 in zip(frames1, labels1):
    try:
        ix = np.where(frames2==frame1)[0][0]
    except:
        print('File not found in out file: %s' % frame1)
        continue
    label1 = classes[int(label1)]
    label2 = classes[int(labels2[ix])]
    if label1 != label2:
        # move image to new folder
        destDir = label1 + '_2_' + label2
        f = str(int(frame1)).zfill(13)
        file = f[:-7] + '_' + f[-7:-5] + '_' + f[-5:] + '.jpg'
        mkdir(destDir)
        try:
            os.rename(label1 + '/' + file, destDir + '/' + file)
            n_move +=1
            print('%d] %s: %s -> %s' % (n_move, file, label1, label2))
        except:
            print('File not found: %s' % file)

print('Num images = %d' % len(frames1))
        
        
 