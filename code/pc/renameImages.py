# renameImages.py -- rename image files to create unique file names

#  renameImages dirIn <date>

import os, sys, re
import datetime
import pandas as pd

if len(sys.argv)>1:
    dirIn = sys.argv[1] + '/'
else:
    print('Please include input folder on command line')
    

if len(sys.argv)>2:
    d = pd.to_datetime(sys.argv[2])
    
else:   
    d = datetime.datetime.today()
    
date = str(d.month).zfill(2) + str(d.day).zfill(2) + str(d.year)[-2:]

run_num = 0    

 # use for multiple folders
#for dir in os.listdir(dirIn): 
#    #file_prefix = date + '_' + str(run_num).zfill(2)
#    file_prefix = dir
#    if dir.find('.') < 0: # check if dir is folder
#        for file in os.listdir(dirIn + dir):
#            if file[-4:] == '.jpg':
#                fnums = re.findall(r'\d+', file)
#                if len(fnums)>1: # use run number and date from file name
#                    run_num = str(fnums[1]).zfill(2)  # single digit run number
#                    fileNew = fnums[0] + '_' + str(run_num).zfill(2) + '_' + fnums[2] +'.jpg'
#                else:  # use other name
#                    fileNew = file_prefix + file[3:]
#                os.rename(dirIn + dir + '/' + file, dirIn + dir + '/' + fileNew)
#                print(file, fileNew)
#    run_num += 1  
    
# use for single folder
for file in os.listdir(dirIn):
    if file[-4:] == '.jpg':
        if file[:6] == '031820':
            file_prefix = '031920_00'
        elif file[:6] == '031920':
            file_prefix = '031920_01'
        elif file[:6] == '032020':
            file_prefix = '032020_00'
        else:
            print('Invalid prefix')
            while True:
                pass
        fileNew = file_prefix + file[-10:]
        os.rename(dirIn + '/' + file, dirIn + '/' + fileNew)
        print(file, fileNew)