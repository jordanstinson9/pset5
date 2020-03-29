###### STILL BUGGY #######

# Python module to unzip and then rename files within the GEO directory
# Requires python package: gzip, shutil
import sys
import os
import gzip
import shutil

# Set base directory
BASE_DIR = os.getcwd()

# Create dictionary of file names for renaming
filenames = {'GSE59635':'illumina2010.txt',
            'GSE59654':'illumina2011.txt',
            'GSE59743':'illumina2012.txt',
            'GSE101709':'illumina2013.txt',
            'GSE101710':'illumina2014.txt'}

# Initialize unpack counter, renaming counter
unpack_i = 0
rename_i = 0

# Move through files in the geo directory and unzip
# Rename the file as a new copy per the dictionary
if os.path.isdir("geotest"):
    geo = os.path.join(BASE_DIR,"geotest")
    for file in os.listdir(geo):
        for name in filenames:
            if file.startswith(name):
                shutil.copyfile(gzip.GzipFile(fileobj=file).read(),
                                open(name.value, 'wb'))
else:
    print("No data found in 'geo' directory, please move data to /geo!")
    exit()

print("Done Unpacking and Renaming!")
print(unpack_i," files unpacked")
print(rename_i," files renamed")
