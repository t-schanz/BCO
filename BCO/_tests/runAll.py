import os
import BCO
import socket

__server = socket.getfqdn()
__server_list = ["mpi","zmaw"]

on_local_machine = False
for s in __server_list:
    if s in __server.lower():
        on_local_machine = True

if not on_local_machine:
    print("Reading Environment Variables...")
    BCO.USE_FTP_ACCESS = True
    BCO.FTP_USER = os.environ["BCO_FTP_USER"]
    BCO.FTP_PASSWD = os.environ["BCO_FTP_PASSWD"]


print("Importing Modules...")
from BCO._tests import ClassTesting, ConverterTesting
from datetime import datetime as dt


print("Creating ClassTesting Instance...")
clstst = ClassTesting(start=dt(2018,3,1),end=dt(2018,3,1),duration=1)

print("Running testEverything()...")
clstst.testEverything()

print("Running ConverterTesting()...")
ConverterTesting()

print("===========================================")
print("$>>> Script runAll.py finished <<<$")
print("===========================================")