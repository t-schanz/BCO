"""
This Module contains the Windlidar class. This class is for easy working with the BCO Windlidar data.
"""

import sys
import bz2
import glob

import MPPy.tools.tools as tools
from MPPy.Instruments.Device_module import __Device,getValueFromSettings

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the MPPy-package to work.")
    sys.exit(1)


class Windlidar(__Device):

    def __init__(self, start, end):

        self.start = self.checkInputTime(start)
        self.end = self.checkInputTime(end)
        self.path = self.__getPath()


    def getVelocity(self):
        pass

    def __getPath(self):
        path = getValueFromSettings("WINDLIDAR_PATH")


    def __getValueFromNc(self, vaelue: str):
        """
        This function gets values from the netCDF-Dataset, which stay constant over the whole timeframe. So its very
        similar to __getArrayFromNc(), but without the looping.

        Args:
            value: A string for accessing the netCDF-file.
                    For example: 'Zf'

        Returns:
            Numpy array
        """
        _date = self.start.date()
        _datestr = self.start.strftime("%Y%m")
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc.bz2" % self.start.strftime("%Y%m%d")
        _file = glob.glob(self.path + _datestr + _nameStr)[0]
        #TODO: Lese die .nc.bz2 dateien ein
        return _file

        return path


