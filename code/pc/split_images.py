import split_folders as split

dirIn='j:/tensorflow/images/denver_logi'
dirOut='j:/tensorflow/images/denver_logi_split'


split.ratio(dirIn, output=dirOut, seed=1337, ratio=(.9, .1)) # default values
