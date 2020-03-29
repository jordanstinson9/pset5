
Listed below are the steps necessary to obtain the files in directory tree src/main/aspera:

1) Download the following files from http://downloads.asperasoft.com/en/downloads/62:

aspera-cli-3.7.2.354.010c3b8-linux-32-release.sh
aspera-cli-3.7.2.354.010c3b8-linux-64-release.sh
aspera-cli-3.7.2.354.010c3b8-mac-10.7-64-release.sh
aspera-cli-3.7.2.354.010c3b8-win-v100-32-release.zip (download only)

3) Create the directory structure for the Aspera files (Windows files are not included):

mkdir -p src/main/aspera/cli/bin/linux
mkdir -p src/main/aspera/cli/bin/linux32
mkdir -p src/main/aspera/cli/bin/osx
mkdir -p src/main/aspera/cli/docs
mkdir -p src/main/aspera/cli/etc

2) Run the downloaded scripts on the different operating systems and copy the appropriate files to directory tree src/main/aspera:

Note: The license, documentation, and ssh files are identical for all operating systems.

Linux x86_64:
------------

chmod 755 aspera-cli-3.7.2.354.010c3b8-linux-64-release.sh
./aspera-cli-3.7.2.354.010c3b8-linux-64-release.sh
find ~/.aspera/cli | sort
cp -p ~/.aspera/cli/bin/ascp src/main/aspera/cli/bin/linux/ascp
cp -p ~/.aspera/cli/docs/license.txt src/main/aspera/cli/docs/license.txt
cp -p ~/.aspera/cli/etc/aspera-license src/main/aspera/cli/etc/aspera-license
cp -p ~/.aspera/cli/etc/asperaweb_id_dsa.openssh src/main/aspera/cli/etc/asperaweb_id_dsa.openssh

Linux x86:
---------

chmod 755 aspera-cli-3.7.2.354.010c3b8-linux-32-release.sh
./aspera-cli-3.7.2.354.010c3b8-linux-32-release.sh
find ~/.aspera/cli | sort
cp -p ~/.aspera/cli/bin/ascp src/main/aspera/cli/bin/linux32/ascp

Mac OS X Intel:
--------------

chmod 755 aspera-cli-3.7.2.354.010c3b8-mac-10.7-64-release.sh
./aspera-cli-3.7.2.354.010c3b8-mac-10.7-64-release.sh
find ~/Applications/Aspera\ CLI | sort
cp -p ~/Applications/Aspera\ CLI/bin/ascp src/main/aspera/cli/bin/osx/ascp


