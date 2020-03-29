# Python module to download HAI data from NIAID Immport database for analysis
# Requires python packages: requests
import sys
import os

# Set base directory
BASE_DIR = os.getcwd()
# print(BASE_DIR) #for troubleshooting

# Change directory Location to import the downloader
# Assumes there is a folder named immport-data-download-tool in the directory
# Throw error if not
if os.path.isdir("immport-data-download-tool"):
    immport_download_code = os.path.join(BASE_DIR,
                                        "immport-data-download-tool",
                                        "bin")
else:
    print("Please download the Immport Data Download Tool.")
    print("Visit: http://www.immport.org/downloads/data/\
download/tool/immport-data-download-tool.zip")
    exit()

# Import the Immport downloader tool
# This requires the python package 'requests' to be installed
sys.path.insert(0,immport_download_code)
os.chdir(immport_download_code)
# print(os.getcwd())  # For troubleshooting

# Import the downloader script
import immport_download

# Return to base directory
os.chdir(BASE_DIR)
# print(os.getcwd())  # for troubleshooting

# Set configurations for downloading
user_name = "izumidk"
password = "20440Project!"

# Need to have output folders nested in directory
# Create the folder for "ImmPort data" --> "immport" if not already there
if os.path.isdir("immport"):
    download_directory = os.path.join(BASE_DIR,"immport")
    print("Immport is already directory!")
else:
    os.mkdir("immport")
    print("Made immport directory!")
    download_directory = os.path.join(BASE_DIR,"immport")

# Download files
# download_file(user_name, password, path to study, download_directory)
# SDY640 - 2014 Data
# SDY520 - 2013 Data
# SDY400 - 2012 Data
# SDY404 - 2011 Data
# SDY63 - 2010 Data
to_download = ['/SDY640/SDY640-DR33_Tab.zip',
                '/SDY520/SDY520-DR33_Tab.zip',
                '/SDY400/SDY400-DR33_Tab.zip',
                '/SDY404/SDY404-DR33_Tab.zip',
                '/SDY63/SDY63-DR33_Tab.zip']

for study in to_download:
    immport_download.download_file(user_name, password,
                                    study, download_directory)
    print "Study", study, "downloaded!"

print("Downloading of HAI data is complete!")
