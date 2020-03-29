# This module will plot the fold-change in gene expression post-Vaccination
# for one patient as an example.
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

# Calculate fold-changes from day 0 to 2, 7, 28
fold_a = []
fold_b = []
fold_c = []
genes = []

# For one patient (first patient), examine whether the day 0 genes were
# significant (p < 0.05), and if so, calculate the fold-changes to the other
# time points.
# NOTE: This may miss some genes that become significant after vaccination,
# but we'll worry about that in the future.
for ind in range(len(array_exp)):
    if (array_exp.iloc[ind,2] < 0.05):
        genes.append(array_exp.iloc[ind,0])
        fold_a.append(np.divide(array_exp.iloc[ind,3],array_exp.iloc[ind,1]))
        fold_b.append(np.divide(array_exp.iloc[ind,5],array_exp.iloc[ind,1]))
        fold_c.append(np.divide(array_exp.iloc[ind,7],array_exp.iloc[ind,1]))

# Convert lists to log2 fold-change
fold_a = np.log2(fold_a)
fold_b = np.log2(fold_b)
fold_c = np.log2(fold_c)

# Add to new data frame
folddata = pd.DataFrame()
folddata['Genes'] = genes
folddata['2d'] = fold_a
folddata['7d'] = fold_b
folddata['28d'] = fold_c
print(folddata.info())

os.chdir(BASE_DIR)

# Move and store results in results directory
if os.path.isdir('results'):
    os.chdir('results')
else:
    os.mkdir('results')
    os.chdir('results')

fig, axs = plt.subplots(1, 1, tight_layout=True, figsize=(6,12))
axs = sns.heatmap(folddata.iloc[:,1:4], cmap='seismic', cbar=True)
axs.set_xlabel('Log$_2$ Fold-Change Post-Vaccination', fontsize='14', fontweight='bold')
axs.set_ylabel('Genes', fontsize='14', fontweight='bold')
axs.set_yticklabels(folddata.iloc[:,0])
plt.savefig('TemporalExpressionChange_2014examplepatient.png')
