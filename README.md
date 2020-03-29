# MIT 20.440 Biological Networks #############################################################################

## Jordan Stinson
## Updated: March 29, 2020
### Problem Set 5: GITHUB upload of example work for term project

## OVERVIEW
This repository contains initial work for the 20.440 project, to compliment
the work by my partner, Izumi de los Rios Kobara. For this project, we intend
to examine how differences in patient response to influenza vaccine may be
explained by their vaccination history, rather than purely differences in the
strain-matching between circulating viruses and those chosen for the vaccine.
Patient immune history, particularly for seasonal influenza given as an annual
vaccine, can influence immune responses to antigens.

For this project, we have two primary types of data--gene expression array
data and antibody titer data (hemagglutination inhibition assay). Our data
has been collected from the National Institutes of Allergy and Infectious
Disease (NIAID) ImmPort public database, which includes a wealth of
immunological data from various studies. We found a 5-year longitudinal study
that includes pre- and post-vaccination titers alongside multi-timepoint PBMC
expression array data for multiple patients (some PBMC results have 18
patients, while other years have up to 89). Together, these data sets should
allow us to determine genes response patterns between different patients,
and correlate to the HAI titers to determine if there are predictive response
patterns. If time allows for this project, we can also perform sequence
analysis on influenza virus strains per season, but that may fall outside of
the scope for this project.

This initial repository contains the scripts developed to download patient
titer data from the NIAID Immport website (download_immport.py), take the
gene expression array data and convert to csv (geo_csv_converter.py), and
perform initial plotting of differential expression with the 2014 data (
plot_multipatient_example.py, plot_temporalfoldchange_example.py). Additional
script to unpack the geo data to text files using python (geo_unpacker.py)
has been included, although is buggy. The gzip -d filename command line was
used to unzip the .gz raw files instead of a script. An example shell script
is under development but is also buggy at this point (e.g. potential ubuntu/
windows issues locally).

The GEO folder is the only folder that should be initially needed to run code
from this repository. New directories will be created as the script modules
are run. Please contact me if there are any questions or issues!

## DATA
The GEO datasets were downloaded after initially searching for influenza
specific data on NIAID ImmPort (via Immunespace.org). We identified studies
of interest from NIAID, given designations of 'SDY' with a number. After
downloading those individual files, it was realized that the SDY files
referenced GEO accession numbers for each of the biosamples.
* immport.org/shared/home
* ncbi.nlm.nih.gov/geo/query/acc.cgi

SDY640: Immunologic and genomic signatures of influenza vaccine
response - 2014
* DOI 10.21430/M3A6GYD5L0
* Year 5 of study; 37 subjects
* EXP14098 HAI Yr5 (280 samples)
* EXP15254 Illumina microarray expression yr5 (79 samples)
  * This corresponds to GEO accession GSE101710
  * 'GSE101710_Expression.raw' renamed 'illumina2014'

SDY520: Immunologic and genomic signatures of influenza vaccine
response - 2013
* DOI 10.21430/M3KVVHM735
* Year 4 of study; 61 subjects
* EXP13937 HAI Yr4 (114 samples)
* EXP15253 Illumina microarray expression PBMC Yr4 (99 samples)
  * This corresponds to GEO accession GSE101709
  * 'GSE101709_Expression.raw' renamed 'illumina2013'

SDY400: Immunologic and genomic signatures of influenza vaccine
response - 2012
* DOI 10.21430/M3U7GDOFIT
* Year 3 of study; 98 subjects
* EXP13550 HAI Yr3 (187 samples)
* EXP13703 Illumina microarray expression PBMC Yr3 (356 samples)
  * This corresponds to GEO accession GSE59743
  * 'GSE59743_non-normalized' renamed to 'illumina2012'
* EXP28412 Proteomics

SDY404: Immunologic and genomic signatures of influenza vaccine
response - 2011
* DOI 10.21430/M3GWQRC8DT
* Year 2 of study; 72 subjects
* EXP13360 HAI Yr2 (138 samples)
* EXP13359 Illumina microarray expression PBMC Yr2 (156 samples)
  * This corresponds to GEO accession GSE59654
  * 'GSE59654_PBMC.raw.corrected' renamed to 'illumina2011'
* EXP13702 Microarray for T and B cells
* EXP13917 Flow cytometry
* EXP28368 Metabolomics
* EXP28414 Proteomics

SDY63: Immunologic and genomic signatures of influenza vaccine
response - 2010
* DOI 10.21430/M38WXGBDTS
* Year 1 of study; 49 subjects
* EXP10608 HAI Yr1 (90 samples)
* EXP10612 Illumina microarray expression PBMC Yr1 (72 samples)
  * This corresponds to GEO accession GSE59635
  * 'GSE59635_non-normalized' renamed to 'illumina2010'
* EXP10613 Microarray for T and B cells
* EXP10614 Microarray for T and B cells

For the two example figures produced through scripts in this repository,
genes with significant expression pre-immunization (p < 0.05) were examined
for their fold-change over time (day 2, day 7, day 28 after vaccination,
log2 converted) in a single patient, or multiple patients were examined
for the changes in expression between day 0 and day 7. I chose to present
only a subset of data as we have high-dimensional data (multiple patients,
multiple PBMC expression timepoints, multiple years) and need to develop a
robust strategy for our analysis.

## FOLDER STRUCTURE
The scripts to perform the initial plotting contain elements to generate new
directories to store information as it is produced, relaxing the requirements
for users to produce the example figures. However, this has only been tested
in an Ubuntu environment on Windows--unclear if there will be issues for Mac
users. At a high level, all initial scripts are contained within the base
directory, with the immport download tool in a sub-directory, and the gene
expression array data in a separate sub-directory 'geo'. As the scripts
included in the repository are executed, new sub-directories will be generated
to contain the HAI data (and other study information) in 'immport', the CSV
files after converting the gene expression data ('data'), and the example
figures in ('results'). So:
**Initial Base Directory** | **Script in Base** | **Final Base Directory**
---------------------------|--------------------|--------------------------
immport-tool | download_immport.py | immport-tool
.|.| immport (created)
geo | geo_csv_converter.py | geo
.|.| data (created)
.| plot_multipatientexample.py | results (created)
.| plot_temporalfoldchange_example.py | results (updated)

## INSTALLATION AND EXECUTION
To download data from NIAID ImmPort, ensure that the immport-data-download-tool
directory is available. If not, running the python script will direct you to
the website URL required for download. Aspera (IBM) software will also be
needed to handle the download (https://www.immport.org/installAsperaHelp).

This data will not be used in the plotting code (Izumi's code handles the HAI
assay data). However, this script can be used to download data from multiple
studies.
* (1) The python packages 'requests' must be installed for the downloader to
work
* (2) Run 'download_immport.py' from terminal/Git Bash
* (3) A directory called 'immport' will be created with the compressed study
files included.

To run the plotting tools for the gene expression array data, ensure that the
GEO data is contained within the geo folder and has already been unzipped to
text files (tab delimited) and renamed 'illuminaYear.txt'. The script only
looks for the renamed files so it will not handle the raw data files (script
in progress to convert raw data to text data, command line was used).
* (1) Pandas, Numpy must be installed
* (2) Run 'geo_csv_converter.py' from terminal/Git bash
* (3) A directory called 'data' will be created with CSV files
* (4) For the plotting scripts, matplotlib and seaborn must be installed
* (5) Run 'plot_multipatient_example.py' to plot a heatmap of the fold-
changes in gene expression for 10 different patients between 7-days post-
vaccination and pre-vaccination expression profiles.
* (6) Run 'plot_temporalfoldchange_example.py' to plot a heatmap of a single
patient's changes in gene expression at day 2, 7, and 28 days after vaccination
relative to their pre-vaccination expression.
* (7) Both plots should be saved to a directory called 'results' that will be
automatically created if it does not already exist.

## REFERENCES
* Hafler, David et al. Defining signatures for immune responsiveness by functional systems immunology. Unpublished.
