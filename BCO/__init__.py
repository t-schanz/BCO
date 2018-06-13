USE_FTP_ACCESS = True
import socket
import os
import configparser

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
version_path = os.path.split(package_directory)[:-1]
import re
VERSIONFILE=os.path.join(*version_path,"_version.py")
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"  # Pattern for finding the version string in the file _version.py
mo = re.search(VSRE, verstrline, re.M)
if mo:
    __version__ = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

# -----------------------------------------------------------
# Import all Modules

from . import Instruments
from . import Quicklooks
from . import tools
from . import settings


__all__ = ["Instruments",
           "Quicklooks",
           "tools"]