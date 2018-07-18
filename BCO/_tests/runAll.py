import os
import BCO

BCO.USE_FTP_ACCESS = True
BCO.FTP_USER = os.environ["BCO_FTP_USER"]
BCO.FTP_PASSWD = os.environ["BCO_FTP_PASSWD"]



from BCO._tests import ClassTesting, ConverterTesting
from datetime import datetime as dt

clstst = ClassTesting(start=dt(2018,5,1),end=dt(2018,5,2),duration=1)

clstst.testEverything()
ConverterTesting()
