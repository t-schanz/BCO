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
    """
    Class for working with the Windlidar Data from the BCO.

    Args:
        start: Either String or datetime.datetime-object indicating the start of the timefwindow
        end: Either String or datetime.datetime-object indicating the end of the timefwindow

    Attributes:
        title: Title of the netCDF file.
        device: Name of the instrument.
        systemID: ID of the instrument.
        scanType: For example "stare".
        focusRange: The focus range.
        temporalResolution: String of the temporal resolution.
        location: Location of the instrument.
    """

    def __init__(self, start, end):

        self.start = self.checkInputTime(start)
        self.end = self.checkInputTime(end)
        self.path = self.__getPath()

        # Attributes:
        self.title = None
        self.device = None
        self.systemID = None
        self.scanType = None
        self.focusRange = None
        self.temporalResolution = None
        self.location = None

        self.__getAttributes()



    def getVelocity(self):
        pass

    def __getPath(self):
        return getValueFromSettings("WINDLIDAR_PATH")

    def __getAttributes(self):
        _date = self.start.date()
        _datestr = _date.strftime("%Y%m")
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc.bz2" % _date.strftime("%Y%m%d")
        _file = glob.glob(self.path + _datestr + "/" +  _nameStr)[0]

        nc = tools.bz2Dataset(_file)

        self.title = nc.title
        self.device = nc.devices
        self.systemID = nc.systemID
        self.scanType = nc.scanType
        self.focusRange = nc.focusRange
        self.temporalResolution = nc.resolution.split(";")[0]
        self.location = nc.location

        nc.close()


    def __getValueFromNc(self, value: str):
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
        _datestr = _date.strftime("%Y%m")
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc.bz2" % _date.strftime("%Y%m%d")
        _file = glob.glob(self.path + _datestr + "/" +  _nameStr)[0]

        nc = tools.bz2Dataset(_file)
        _var = nc.variables[value][:].copy()
        nc.close()

        return _var




