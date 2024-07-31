import os, sys

# Get input parameters from command line
if len(sys.argv) > 1:
    dirIn = sys.argv[1]
    if dirIn[-1] != '/':
        dirIn += '/'
else:
    raise Exception('Input Folder Missing')
    
for dir in os.listdir(dirIn):
    os.system('python3 sortImages.py %s -nosort' % (dirIn + dir))