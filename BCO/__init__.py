USE_FTP_ACCESS = True
import socket
import os
import configparser
# -----------------------------------------------------------

# Trying to make a guess for using ftp-acces:

__server = socket.getfqdn()
__server_list = ["mpi","zmaw"]

for s in __server_list:
    if s in __server.lower():
        USE_FTP_ACCESS = False

# -----------------------------------------------------------
package_directory = os.path.dirname(os.path.abspath(__file__))

# Setting up the config parser:
config = configparser.RawConfigParser()
config.read(package_directory+"/settings.ini")


# ----------------------------------------------------------

# Setting global variables for FTP:
FTP_USER = None
FTP_PASSWD = None
FTP_SERVER = config["DEFAULT"]["SERVER_NAME"]

# -----------------------------------------------------------
from . import Instruments
from . import Quicklooks
from . import tools
from . import settings


__all__ = ["Instruments",
           "Quicklooks",
           "tools"]