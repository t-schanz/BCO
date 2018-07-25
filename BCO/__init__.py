USE_FTP_ACCESS = True
import socket
import os
import configparser
import re

# -----------------------------------------------------------
# Trying to make a guess for using ftp-access:
__server = socket.getfqdn()
__server_list = ["mpi","zmaw"]

for s in __server_list:
    if s in __server.lower():
        USE_FTP_ACCESS = False

# -----------------------------------------------------------
# Setting up the config parser:

package_directory = os.path.dirname(os.path.abspath(__file__))

config = configparser.RawConfigParser()
config.read(package_directory+"/settings.ini")


# ----------------------------------------------------------
# Setting global variables for FTP:

FTP_USER = None
FTP_PASSWD = None
FTP_SERVER = config["DEFAULT"]["SERVER_NAME"]

# ----------------------------------------------------------
# Setting the version:

# try:
#     version_path = os.path.split(package_directory)
#     print("Version: ", version_path)
#     print("Package: ", package_directory )
#     VERSIONFILE=os.path.join(version_path[0],"_version.py")
#     print("FILE: " ,VERSIONFILE)
#     verstrline = open(VERSIONFILE, "rt").read()
# except:
#     VERSIONFILE = os.path.join(package_directory, "_version.py")
#     verstrline = open(VERSIONFILE, "rt").read()
# VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"  # Pattern for finding the version string in the file _version.py
# mo = re.search(VSRE, verstrline, re.M)
# if mo:
#     __version__ = mo.group(1)
# else:
#     raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# -----------------------------------------------------------
# Import all Modules

from . import Instruments
from . import Quicklooks
from . import tools
from . import settings
from . import _tests


__all__ = ["Instruments",
           "Quicklooks",
           "tools"]