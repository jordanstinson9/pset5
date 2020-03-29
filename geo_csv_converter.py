# This module converts the downloaded GEO text files for the gene expression
# array data from each SDY text file into CSV format. This enables users to
# examine the data in Excel and easier import to pandas dataframe in later
# script modules.
# Requires Python packages: pandas, numpy
import sys
import os
import pandas as pd
import numpy as np

# Get base directory
BASE_DIR = os.getcwd()

# Change to the data download directory
# Assumes downloaded files are in the /geo folder
if os.path.isdir("geo"):
    geo = os.path.join(BASE_DIR,"geo")
else:
    print("Please download/move the GEO text data to the '/geo' directory")
    exit()

# Import data into pandas dataframe and save as csv files in /data folder
# Check that /data folder exists
if not os.path.isdir('data'):
    os.mkdir('data')

# Now loop through files in the directory and convert to CSV
# Initialize conversion counter
converted = 0
for file in os.listdir(geo):
    #Initialize an empty array
    templist = []
    os.chdir(BASE_DIR); os.chdir(geo)

    if file.startswith("i"):
        tempdata = pd.read_table(file, sep='\t')
        csvtitle = str(file).replace('txt','csv')
        os.chdir(BASE_DIR)
        tempdata.to_csv(os.path.join('data',csvtitle),index=False)
        converted += 1

if converted > 0:
    print(converted, 'files successfully converted to CSV!')
else:
    print("Please check files are named illuminaYEAR.txt")
