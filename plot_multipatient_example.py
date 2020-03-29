# This module will plot the fold-change in gene expression post-Vaccination
# for multiple patients at one time point comparison (day 0 to day 7)
# Python packages required: pandas, numpy, matplotlib, seaborn
# The matplotlib.use line is required for Ubuntu to work on Windows
import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

# Set base directory
BASE_DIR = os.getcwd()

# Change to the data directory
# Assumes downloaded files are in the /data folder
data = os.path.join(BASE_DIR,"data")
os.chdir(data)

# Read data to csv (include headers in the dataframe)
array_exp = pd.read_csv("illumina2014.csv", header=0)
print(array_exp.info())

# Dictionary of day 0 and day 7 columns
# Neccessary for now because patient 2 only has 3 timepoints (the rest have 4)
day0 = {'Patient 1':1,
        'Patient 2':15,
        'Patient 3':23,
        'Patient 4':31,
        'Patient 5':39,
        'Patient 6':47,
        'Patient 7':55,
        'Patient 8':63,
        'Patient 9':71,
        'Patient 10':79}
day7 = {'Patient 1':5,
        'Patient 2':19,
        'Patient 3':27,
        'Patient 4':35,
        'Patient 5':43,
        'Patient 6':51,
        'Patient 7':59,
        'Patient 8':67,
        'Patient 9':75,
        'Patient 10':83}

#Create empty data frame for results
folddata = pd.DataFrame()

# For each patient of 10 example subjects, examine whether the day 0 genes were
# significant (p < 0.05), and if so, calculate the fold-changes to day 7.
# NOTE: This may miss some genes that become significant after vaccination,
# but we'll worry about that in the future. Also assumes the same genes are
# significant between patients, but this will also be addressed in the future.
for patient in day0:
    fold_change = [] #initialize empty list
    for ind in range(len(array_exp)):
        if (array_exp.iloc[ind,2] < 0.05):
            fold_change.append(np.divide(array_exp.iloc[ind,day0[patient]],
                                array_exp.iloc[ind,day7[patient]]))

    folddata[patient] = np.log2(fold_change)
    print(patient, "Added to dataframe")


print(folddata.info())

os.chdir(BASE_DIR)

# Move and store results in results directory
if os.path.isdir('results'):
    os.chdir('results')
else:
    os.mkdir('results')
    os.chdir('results')

# Plot results
fig, axs = plt.subplots(1, 1, tight_layout=True, figsize=(12,12))
axs = sns.heatmap(folddata.iloc[:,0:11], cmap='seismic', cbar=True)
axs.set_xlabel('Log$_2$ Fold-Change 7 Days After Vaccination',
                fontsize='14', fontweight='bold')
axs.set_ylabel('Genes', fontsize='14', fontweight='bold')
plt.savefig('Day7ExpressionChange_2014multiplepatients.png')
