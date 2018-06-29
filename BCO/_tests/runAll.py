from BCO._tests import ClassTesting, ConverterTesting
from datetime import datetime as dt

clstst = ClassTesting(start=dt(2018,5,1),end=dt(2018,5,2),duration=1)

clstst.testEverything()
ConverterTesting()
