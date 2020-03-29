#!/bin/bash
#
# This script downloads an ImmPort data file or directory when valid credentials are provided.
#

###########################################################################################################################################

#
# This subroutine deletes temporary files.
#
clean() {
  if
    [ -d $tmp_dir -o -d $log_dir ]
  then
    echo ""
    echo "Cleaning the following files:"
    echo ""
  fi
  if
    [ -d $tmp_dir ]
  then
    find $tmp_dir | sort
    /bin/rm -rf $tmp_dir
  fi
  if
    [ -d $log_dir ]
  then
    find $log_dir | sort
    /bin/rm -rf $log_dir
  fi
}

#
# This subroutine displays the version.
#
version() {
  echo ""
  cat `dirname $0`/version.txt
  echo ""
}

###########################################################################################################################################

#
# This function converts the list of files and directories to be downloaded to a JSON string in the format expected by the ImmPort Data API
#
generate_json_input_data() {
  download_manifest_text_file="$1"
  download_manifest_json_file="$2"
  if
    [ $debug = 1 ]
  then
    echo ""
    echo "Generating JSON input data from text file $download_manifest_text_file and saving it in file $download_manifest_json_file"
  fi
  /bin/rm -f $download_manifest_json_file
  echo -n "{ \"paths\" : [ " >> $download_manifest_json_file
  first=1
  exec < $download_manifest_text_file 
  while 
    read file_name
  do
    if
      [ $first = 0 ]
    then
      echo -n ", " >> $download_manifest_json_file
    else
      first=0
    fi
    echo -n "\"$file_name\"" >> $download_manifest_json_file
  done
  echo " ] }" >> $download_manifest_json_file
}

###########################################################################################################################################

#
# This function converts the list of files and directories to be downloaded to pairs of source and destination to be passed to the Aspera
# command-line tool
#
generate_aspera_input_data() {
  download_manifest_text_file="$1"
  download_pairs_file="$2"
  if
    [ $debug = 1 ]
  then
    echo ""
    echo "Generating pairs of source and destination from text file $download_manifest_text_file and saving them in file $download_pairs_file"
  fi
  /bin/rm -f $download_pairs_file
  exec < $download_manifest_text_file 
  while 
    read file_name
  do
    echo "$file_name" >> $download_pairs_file                        # source
    echo "${destination_root}${file_name}" >> $download_pairs_file   # destination
  done
}

###########################################################################################################################################

#
# Main Program
#

#
# Initialize variables
#
script_dir=`dirname $0`
script_name=`basename $0`
script_basename=`echo $script_name | sed -e 's/\.sh//'`
tmp_dir="$script_dir/../tmp"
output_file="$tmp_dir/$script_basename.output"
error_file="$tmp_dir/$script_basename.error"
log_dir="$script_dir/../log"
log_file="$log_dir/$script_basename.log"
destination_root="."
download_manifest_text_file="$tmp_dir/${script_basename}Manifest.txt"
download_manifest_json_file="`echo $download_manifest_text_file | sed -e 's/\.txt/.json/'`"
download_pairs_file="$tmp_dir/${script_basename}Pairs.txt"

aspera_server="aspera-immport.niaid.nih.gov"
aspera_username="databrowser"
aspera_bin_dir_base="$script_dir/../aspera/cli/bin"
aspera_etc_dir="$script_dir/../aspera/cli/etc"
aspera_license_file="$aspera_etc_dir/aspera-license"
aspera_private_key_file="$aspera_etc_dir/asperaweb_id_dsa.openssh"
aspera_log_file="$log_dir/aspera-scp-transfer.0.log"


if
  [ "$IMMPORT_TOKEN_URL" = "" ]
then
  immport_token_url="https://auth.immport.org/auth/token"
else
  immport_token_url="$IMMPORT_TOKEN_URL"
fi
if
  [ "$IMMPORT_DATA_API_BASE_URL" = "" ]
then
  immport_data_api_base_url="https://api.immport.org/data"
else
  immport_data_api_base_url="$IMMPORT_DATA_API_BASE_URL"
fi

if
  [ "`echo $immport_token_url | fgrep immport.org`" = "" -o "`echo $immport_data_api_base_url | fgrep immport.org`" = "" ]
then
  curl_command="curl -k"
else
  curl_command="curl"
fi

#
# Validate input parameters
#
usage="\

usage: `basename $0` username password file | --manifest-file=filename [ --verbose | --debug ]
       `basename $0` --clean

where

  username = ImmPort username
  password = ImmPort password
  file     = Name of file or directory to be downloaded (e.g. /ALLSTUDIES/ALLSTUDIES-DR22_table_count.txt).
             If this parameter is not specified, then the --manifest-file option must be specified.

  --manifest-file=filename = A manifest file containing the list of files and directories to be downloaded.
                             The filename can be either a text file or a JSON file.  If it is a text file,
                             it must contain one file or directory name per line.  If it is a JSON file,
                             it must have a .json file extension AND conform to the output of the
                             ImmPort Shared Data Query API.  If this option is not specified, then parameter
                             'file' must be specified.

  --verbose = run in verbose mode
  --debug   = run in debug mode (for troubleshooting purposes)
  --clean   = clean output, error, and log files
  --version = display the version 
"

if
  [ $# -eq 1 -a "$1" = "--clean" ]
then
  clean
  exit 0
fi

if
  [ $# -eq 1 -a "$1" = "--version" ]
then
  version
  exit 0
fi


debug=0
verbose=0
if
  [ $# -lt 3 ]
then
  echo "$usage"
  exit 1
fi
username="$1"
password="$2"
file="$3"
if
  [ $# -gt 3 -a "$4" ]
then
  if
    [ "$4" = "--verbose" ]
  then
    verbose=1
  else
    if
      [ "$4" = "--debug" ]
    then
      debug=1
    else 
      echo "$usage"
      exit 1
    fi
  fi
fi

#
# Check if a manifest file was specified
#
if
  [ "`echo $file | grep '^.-manifest-file='`" != "" ]
then
  #
  # A manifest file was specified
  #
  # Check if the file exists and is readable
  #
  manifest_file="`echo $file | sed -e 's/^.-manifest-file=//'`"
  if
    [ ! -r $manifest_file ]
  then
    echo ""
    echo "*** File $manifest_file does not exist or is not readable. ***"
    echo ""
    exit 1
  else
    # 
    # Check the file extension
    #
    if
      [ "`echo $manifest_file | grep '\.json$'`" != "" ]
    then
      #
      # The manifest file is a JSON file
      #
      # Check if the format conforms to the output of the ImmPort Shared Data Query API
      #
      if
        [ "`cat $manifest_file | fgrep '"filePath"' | cut -d: -f2 | sed -e 's/^ *"//;s/" *$//' | sort -u`" = "" ]
      then
        echo ""
        echo "*** File $manifest_file is a JSON file but does not conform to the output of the ImmPort Shared Data Query API. ***"
        echo ""
        exit 1
      fi
    fi
  fi
fi

#
# Verify that all required files exist
#
if
  [ ! -x $aspera_ascp_command ]
then
  echo "ERROR: File $aspera_ascp_command does not exist or is not executable"
  exit 1
fi
if
  [ ! -r $aspera_license_file ]
then
  echo "ERROR: File $aspera_license_file does not exist or is not readable"
  exit 1
fi

if
  [ ! -r $aspera_private_key_file ]
then
  echo "ERROR: File $aspera_private_key_file does not exist or is not readable"
  exit 1
fi

#
# Create the appropriate directories
#
if
  [ ! -d $tmp_dir ]
then
  mkdir -p $tmp_dir
fi
if
  [ ! -d $log_dir ]
then
  mkdir -p $log_dir
fi

#
# Create a text file with the list of files and directories to be downloaded
#
if
  [ "`echo $file | grep '^.-manifest-file='`" = "" ]
then
  #
  # A manifest file was NOT specified
  #
  echo "$file" > $download_manifest_text_file
else
  #
  # A manifest file was specified
  #
  if
    [ "`echo $manifest_file | grep '\.json$'`" = "" ]
  then
    #
    # The manifest is NOT a JSON file
    #
    cp -p $manifest_file $download_manifest_text_file
  else
    #
    # The manifest is a JSON file
    #
    # Extract the file names from the JSON file
    #
    cat $manifest_file | fgrep '"filePath"' | cut -d: -f2 | sed -e 's/^ *"//;s/" *$//' | sort -u > $download_manifest_text_file
  fi
fi

#
# Get the operating system, architecture, and command to execute
#
os_name=`uname -s`
if
  [ "$os_name" = "Linux" ]
then
  hardware_name=`uname -m`
  if
    [ "$hardware_name" = "x86_64" ]
  then
    bin_dir="$aspera_bin_dir_base/linux"
  else
    bin_dir="$aspera_bin_dir_base/linux32"
  fi
else
  if
    [ "$os_name" = "Darwin" ]
  then
    bin_dir="$aspera_bin_dir_base/osx"
  else
    echo "ERROR: Unsupported operating system: $os_name"
    exit 1
  fi
fi
aspera_ascp_command="$bin_dir/ascp"

#
# Display the input parameters and configuration
#
if
  [ $debug = 1 ]
then
  echo ""
  echo ">>> Displaying input parameters"
  echo ""
  echo "username                      = $username"
  echo "password                      = PROTECTED"
  if
    [ "$manifest_file" = "" ]
  then
    echo "file                          = $file"
  else
    echo "manifest_file                 = $manifest_file"
  fi
  echo ""
  echo ">>> Displaying configuration"
  echo ""
  echo "tmp_dir                       = $tmp_dir"
  echo "output_file                   = $output_file"
  echo "error_file                    = $error_file"
  echo ""
  echo "log_dir                       = $log_dir"
  echo "log_file                      = $log_file"
  echo ""
  echo "immport_token_url             = $immport_token_url"
  echo "immport_data_api_base_url     = $immport_data_api_base_url"
  echo ""
  echo "aspera_server                 = $aspera_server"
  echo "aspera_user_name              = $aspera_username"
  echo "aspera_bin_dir_base           = $aspera_bin_dir_base"
  echo "aspera_etc_dir                = $aspera_etc_dir"
  echo "aspera_private_key_file       = $aspera_private_key_file"
  echo "aspera_ascp_command           = $aspera_ascp_command"
fi

#
# Get the ImmPort token
#
command="$curl_command \"$immport_token_url\" -X POST --header 'Accept: application/json;charset=UTF-8' --data \"username=$username&password=$password\""
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo ">>> Getting the ImmPort token"
  echo ""
  echo "$command" | sed -e 's/password=[^"]*/password=PROTECTED/'
fi
/bin/rm $error_file $output_file 2> /dev/null
eval "$command" 2> $error_file > $output_file
if
  [ -s $error_file -a ! -s $output_file ]
then
  cat $error_file | fgrep 'curl' | sed -e 's/^.*curl/ERROR: curl/'
  exit 1
fi
command="cat $output_file | fgrep '\"token\"' | sed -e 's/^.*\"token\" : \"//;s/\".*$//'"
if
  [ $debug = 1 ]
then
  echo ""
  echo ">>> Extracting the ImmPort token"
  echo ""
  echo "$command"
fi
immport_token=`eval "$command"`
if
  [ $debug = 1 ]
then
  echo ""
  echo "immport_token = $immport_token"
fi
if
  [ "$immport_token" = "" ]
then
  if
    [ "`cat $output_file | grep -i "bad.*credentials"`" != "" ]
  then
    echo "ERROR: Bad credentials"
  else
    echo "ERROR: ImmPort token could not be obtained"
  fi
  exit 1
fi

#
# Convert the list of files and directories to be downloaded to a JSON string in the format expected by the ImmPort Data API
#
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo ">>> Converting the list of files and directories below to a JSON string in the format expected by the ImmPort Data API"
  echo ""
  cat $download_manifest_text_file
fi
generate_json_input_data "$download_manifest_text_file" "$download_manifest_json_file"
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  cat $download_manifest_json_file
fi

#
# Get the Aspera token
#
command="$curl_command --header \"Authorization: bearer $immport_token\" --header \"Content-Type: application/json\" -X POST \"$immport_data_api_base_url/download/token\" --data \"@${download_manifest_json_file}\""
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo ">>> Getting the Aspera token from the ImmPort Data API to download the files and directories listed below:"
  echo ""
  cat $download_manifest_text_file
  echo ""
  echo "$command"
fi

/bin/rm $error_file $output_file 2> /dev/null
eval "$command" 2> $error_file > $output_file
if
  [ -s $output_file ]
then
  error_line="`cat $output_file | grep '"error" *:'`"
  if
    [ "$error_line" != "" ]
  then
    error_message=`cat $output_file | grep '"message" *:' | sed -e 's/^.*"message" *: *"//;s/".*$//'`
    echo ""
    echo "ERROR: $error_message"
    echo ""
    exit 1
  fi
fi
command="cat $output_file | fgrep '\"token\"' | sed -e 's/^.*\"token\" *: *\"//;s/\".*$//'"
if
  [ $debug = 1 ]
then
  echo ""
  echo ">>> Extracting the Aspera token"
  echo ""
  echo "$command"
fi
aspera_token=`eval "$command"`
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo "aspera_token = $aspera_token"
fi

if
  [ "$aspera_token" = "" ]
then
  echo "ERROR: Aspera token could not be extracted from curl command output"
  exit 1
fi

#
# Convert the list of files and directories to be downloaded to pairs of source and destination to be passed to the Aspera command-line tool
#
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo ">>> Converting the list of files and directories below to pairs of source and destination to be passed to the Aspera command line tool"
fi
generate_aspera_input_data "$download_manifest_text_file" "$download_pairs_file"
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  cat $download_pairs_file
fi

#
# Download the files or directories
#
command="$aspera_ascp_command -v -L $log_dir -i $aspera_private_key_file -O 33001 -P 33001 -W \"$aspera_token\" --user=\"$aspera_username\" --host=\"${aspera_server}\" --mode=\"recv\" -p --file-pair-list=\"${download_pairs_file}\" ."
if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
  echo ">>> Downloading the following files and directories:"
  echo ""
  cat $download_manifest_text_file
  echo ""
  echo "$command"
  echo ""
fi

$aspera_ascp_command -v -L $log_dir -i $aspera_private_key_file -O 33001 -P 33001 -W "$aspera_token" --user="$aspera_username" --host="${aspera_server}" --mode="recv" -p --file-pair-list="${download_pairs_file}" .

if
  [ $debug = 1 -o $verbose = 1 ]
then
  echo ""
fi

exit 0
