# db_filter.py -- run filter from image database using metadata

import os, shutil
import pandas as pd

DATABASE = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/LA_metadata.db'
IMAGE_DIR = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Cropped/'
OUT_DIR = 'D:/consulting/Pathwise/ImageFiles/LosAngeles/Filter/'

# Load database
df = pd.read_feather(DATABASE) 

# Create output folder
try:
  shutil.rmtree(OUT_DIR)
except:
    pass
os.mkdir(OUT_DIR)


res = df.loc[((df.roll/100)**2 + (df.pitch/100)**2) > 10]
print('Found %d files' % len(res))


# copy images to filter folder
for image, folder in zip(res.image, res.folder):
    x = str(image).zfill(13)
    date = x[0:6]
    file = x[0:6] + '_' + x[6:8] + '_' + x[8:] + '.jpg'
    shutil.copy(IMAGE_DIR + date + '/' + str(folder) + '/' + file,
                OUT_DIR + file)
