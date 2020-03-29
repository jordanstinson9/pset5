#!/bin/bash
## This example shell script should execute the script modules to convert
## the geo data to CSV files, then plot the two example figures with the
## 2014 data.
### To convert text files to CSV
chmod +x geo_csv_converter.py
python geo_csv_converter.py
### To plot the temporal gene expression results for 1 patient
chmod +x plot_temporalfoldchange_example.py
python plot_temporalfoldchange_example.py
### To plot the multipatient example for 7-day fold-change
chmod +x plot_multipatientexample.py
python plot_multipatientexample.py
### These modules are still under construction/are buggy in Ubuntu
# chmod +x geo_unpacker.py
# python geo_unpacker.py
