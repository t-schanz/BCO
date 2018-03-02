USE_FTP_ACCESS = True
import socket
import os
# -----------------------------------------------------------

# Trying to make a guess for using ftp-acces:

__server = socket.getfqdn()
__server_list = ["mpi","zmaw"]

for s in __server_list:
    if s in __server.lower():
        USE_FTP_ACCESS = False

# ----------------------------------------------------------

# Setting global variables for FTP:
FTP_USER = None
FTP_PASSWD = None
FTP_SERVER = None

package_directory = os.path.dirname(os.path.abspath(__file__))

with open(package_directory + "/ftp_settings.ini") as f:
    lines = f.readlines()

    for line in lines:
        if "SERVER_NAME:" in line:
            FTP_SERVER = line.split(":")[1].rstrip()

# -----------------------------------------------------------
from . import Instruments
from . import Quicklooks
from . import tools
from . import settings


__all__ = ["Instruments",
           "Quicklooks",
           "tools"]