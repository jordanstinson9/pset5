#!/usr/bin/env python3
'''
************************
ImmPort Download Library
************************

Download data from the ImmPort DataBrowser site using Aspera. This module was
designed to be used as a module within another Python 3 program or as a
command line program to download a file from the ImmPort DataBrowser site.

By default the logging level is set to "Warning", which will not produce
messages, unless there is a real problem. If you would like a more detailed
output, set the logging level to "Info".

Command line usage
------------------

::

  immport-download.py
                --file_path /ALLSTUDIES/ALLSTUDIES-DR21_Metadata/study.txt
                --user_name "USERNAME"
                --password 'PASSWORD' (Optional, if missing prompted)
                --output_directory (Default: ../output)

Module usage
-------------

::

  import immport_download
  immport_download.download_file(user_name,password,
                                    file_path,output_directory)


This module is dependent on the ASPERA client libraries. By default this
library connects to the ASPERA server on port 33001. If you have trouble
making a connection to this port, you may need to talk to your local network
administrator to open this port in the firewall.
'''

import sys
import os
import json
import logging
import platform
import requests
import subprocess
import argparse
import getpass

#
# Set logging handler in case it is used as a module
#
logging.getLogger(__name__).addHandler(logging.NullHandler())

#
# Setup defaults
#
module_path = os.path.dirname(__file__)
TOKEN_URL = "https://auth.immport.org/auth/token"
DATA_URL = "https://api.immport.org/data"
ASPERA_BIN_DIR = module_path + "/../aspera/cli/bin"
ASPERA_PRIVATE_KEY_FILE = module_path + \
    "/../aspera/cli/etc/asperaweb_id_dsa.openssh"
ASPERA_USERNAME = "databrowser"
ASPERA_SERVER = "aspera-immport.niaid.nih.gov"


class DownloadException(Exception):
    pass


class PasswordAction:
    '''
    Class to handle case where password not entered on the command line
    '''
    DEFAULT = "No Password Entered"

    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass("Enter Password:")
        self.value = value

    def __str__(self):
        return self.value

#
# The following methods support the main program, but can also
# be used independently as library methods.
#


def download_file(user_name, password, file_path, output_directory):
    '''Download a file by first checking ImmPort user credentials,
       checking the file_path exists, retrieving an Aspera token, then
       executing the Aspera command line program to retrieve the file.

       :param user_name: ImmPort user name.
       :param password: ImmPort user password.
       :param file_path: Path to the file on the ImmPort DataBrowser site.
       :param output_directory: Location of the file system to place the
                                the downloaded file.

       return: None
    '''
    immport_token = request_immport_token(user_name, password)
    if immport_token is None:
        logging.info(
            "ERROR: Credentials incorrect for ImmPort, unable to retrieve token")
        raise DownloadException(
            "ERROR: Credentials incorrect for ImmPort, unable to retrieve token")
    aspera_token = request_aspera_token(file_path, immport_token)
    if aspera_token is None:
        logging.info("ERROR: Unable to obtain Aspera token")
        raise DownloadException("ERROR: Unable to obtain Aspera token")

    retrieve_file(file_path, output_directory, aspera_token)


def request_aspera_token(file_path, immport_token):
    '''Request an Aspera token

       param file_path: Path to the file on the ImmPort Databrowswer site.
       param immport_token: Token obtained from ImmPort authentication.

       return aspera_token
    '''
    url = DATA_URL + "/download/token"
    headers = {
        'Authorization': "bearer " + immport_token,
        'Content-Type': "application/json"
    }

    payload = '{ "paths" : [ "' + file_path + '" ] }'
    r = requests.post(url, headers=headers, data=payload)
    if r.status_code == 200:
        return r.json()['token']
    else:
        return None


def request_immport_token(user_name, password):
    '''Request an ImmPort token

       :param user_name: ImmPort user name.
       :param password: ImmPort user password.

       return immport_token
    '''
    r = requests.post(TOKEN_URL,
                      data={'username': user_name, 'password': password})
    if r.status_code == 200:
        return r.json()['token']
    else:
        return None


def api(url,immport_token):
    '''Make API Query request

       param url: Query API url
       param immport_token: Token obtained from ImmPort authentication.

       return results
    '''
    headers = {
        'Authorization': "bearer " + immport_token
    }

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.text
    else:
        return None


def retrieve_file(file_path, output_directory, aspera_token):
    '''Retrieve file from ImmPort DataBrowser site using Aspera client
       library.

       :param file_path: Path to the file on the ImmPort DataBrowser site.
       :param output_directory: Location of the file system to place the
                                the downloaded file.
       :param aspera_token: Aspera token obtained from ImmPort

       return None
    '''

    #
    # Determine the correct executable for the operating system.
    # Currently support Linux 32/64 and Apple/Darwin.
    #
    os_name = platform.system()
    command = ""
    if os_name == "Linux":
        hardware_name = platform.machine()
        if hardware_name == "x86_64":
            command = ASPERA_BIN_DIR + "/linux/ascp"
        else:
            command = ASPERA_BIN_DIR + "/linux32/ascp"
    elif os_name == "Darwin":
        command = ASPERA_BIN_DIR + "/osx/ascp"
    else:
        logging.warning("ERROR: Unsupported operting system: " + os_name)
        raise DownloadException("ERROR: Unsupported operatin system: "
                                + os_name)

    command += " -v -L " + output_directory + " -i " + \
        ASPERA_PRIVATE_KEY_FILE + " -O 33001 -P 33001 -W "

    command += '"' + aspera_token + '" --user ' + ASPERA_USERNAME + ' -p '
    command += ASPERA_SERVER + ":'" + file_path + "' " + output_directory
    subprocess.call(command, shell=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
             prog="immport-download",
             description="Download data from the ImmPort DataBrowser")

    parser.add_argument(
        '--file_path',
        dest="file_path",
        required=True,
        help="Specify the path to the file"
    )

    parser.add_argument(
        '--user_name',
        dest="user_name",
        required=True,
        help="Enter the ImmPort user name"
    )

    parser.add_argument(
        '--password',
        dest="password",
        type=PasswordAction,
        default=PasswordAction.DEFAULT,
        help="Enter the Immport password"
    )

    parser.add_argument(
        '--output_directory',
        dest="output_directory",
        default="../output",
        required=False,
        help="Specify the output directory"
    )

    parser.add_argument(
        '--log',
        dest="loglevel",
        default="WARNING",
        required=False,
        help="Specify the log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    args = parser.parse_args()
    #
    # Setup Logging
    #
    logging.basicConfig(format='%(levelname)s:%(module)s:%(message)s',
                        level=args.loglevel)
    log = logging.getLogger(__name__)

    try:
        download_file(args.user_name, args.password,
                      args.file_path, args.output_directory)
    except DownloadException as ex:
        print(ex)
        sys.exit(1)
    sys.exit(0)
