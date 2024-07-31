# unsortImages.py --  Move images back from sorted sub-folders into main 
#                     folder and save file locations to sort_result.txt 
#
# updateImageLabels.py inputFolder <-nosort>
#
#    -nosort: create sort file but don't move images
#
import os, sys
import numpy as np

# Define output file formats 
outf = {'frame' : 0, 'label' : 1, 'class' : 2, 'swFlag' : 8, 'pos' : 9, 'vel' : 12}

 
# define image classes, these must be alphabetical to match keras API 
label_dict = {'bike_lane' : 0, 'crosswalk' : 1, 'side' : 2, 'street' : 3, 'unknown' : 4}


# Get input folder from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
else:
    raise Exception('No input folder specified on command line')
nosort = 0
if len(sys.argv) > 2:
    if sys.argv[2] == '-nosort':
        nosort = 1
        
os.chdir(dirIn)
    
 
# loop through images in each sub-folder and move to main folder
#label_dict.update({'unknown' : -1})  # include images from unknown class
labels = label_dict.keys()
ix = 0
sort = []
for label in labels:
    if os.path.exists(label):
        print(label)
        fnames1 = sorted([fname for fname in os.listdir(label)])
        for file in fnames1: # known images (xxxxx)
            if file[-4:] == '.jpg':
                img_num = file[-19:-13] + file[-12:-10] + file[-9:-4]
                try:
                    if nosort == 0:
                        os.rename(label + '/' + file, file)
                    sort.append((int(img_num), label_dict[label]))
                    ix += 1
                    print(file)
                except:  # indicates duplicate image number
                    print('%s: %s' % (sys.exc_info()[0], file))
                    
    if os.path.exists('_' + label):
        print(label)
        fnames2 = sorted([fname for fname in os.listdir('_' + label)])
        for file in fnames2: # uncertain images (_xxxxx)
            if file[-4:] == '.jpg':
                #img_num = file[-9:-4]
                img_num = file[-19:-13] + file[-12:-10] + file[-9:-4]
                try:
                    if nosort == 0:
                        os.rename('_' + label + '/' + file, file)
                    sort.append((int(img_num), label_dict[label]))
                    ix += 1
                    print(file)
                except:  # indicates duplicate image number
                    print('%s: %s' % (sys.exc_info()[0], file))

np.savetxt('sort_results.txt', sort, fmt='%d,%d', delimiter=',')        
        
    

