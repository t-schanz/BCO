"""
This Module contains the Windlidar class. This class is for easy working with the BCO Windlidar data.
"""

import sys
import bz2
import glob
import numpy as np
from datetime import timedelta

import BCO.tools.tools as tools
from BCO.Instruments.Device_module import __Device,getValueFromSettings
import BCO

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)

# TODO: DAS WINDLIDAR IST MOMENTAN NOCH NICHT VIA FTP ERREICHBAR.
# TODO: SOBALD DAS GEÄNDERT IST MUSS HIER NOCH EINIGES ANGEPASST WERDEN WAHRSCHEINLICH!
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

    Example:
        The following example initiates a Windlidar class with data from the whole day of 21.06.2017:

        >>> lidar = Windlidar(start="20170621", end="20170621")

        Another timespan could be from the 21.06.2017 15:30 UTC to 23.06.2017 18:41 UTC:

        >>> lidar = Windlidar(start="201706211530", end="20170623061841")


        With the initiated class you can then load data, for example the vertical velocity:

        >>> lidar = Windlidar(start="20170621", end="20170621")
        >>> velocity = lidar.getVelocity()

        It is possible to directly get the variable by chaining the initialisation and the function.
        The following example produces the exact same result as the one before:

        >>> velocity = Windlidar(start="20170621", end="20170621").getVelocity()


    """

    def __init__(self, start, end):

        self.start = self._checkInputTime(start) + timedelta(hours=0)
        self.end = self._checkInputTime(end) + timedelta(hours=0)

        self.skipped = None  # needed to store skipped dates.

        self._instrument = "WINDLIDAR"  # String used for retrieving the filepath from settings.ini
        self._name_str = "WindLidar__Deebles_Point*__%s.nc*" % ("#")  # general name-structure of file.
                                                            # "#" indicates where date will be replaced
        self._dateformat_str = "%Y%m%d"  # the datetime format this instrument uses
        self._ftp_files = []

        if BCO.USE_FTP_ACCESS:
            for _date in tools.daterange(self.start.date(), self.end.date()):
                _datestr = _date.strftime(self._dateformat_str)
                _nameStr = self._name_str.replace("#", _datestr)
                print(_nameStr)
                self.path = self._downloadFromFTP(ftp_path=getValueFromSettings("RADAR_PATH"), file=_nameStr)

        else:
            self.path = self.__getPath()
        # print(self.path)

        # Attributes:
        self.title = None
        self.device = None
        self.systemID = None
        self.scanType = None
        self.focusRange = None
        self.temporalResolution = None
        self.location = None
        self.lat = None
        self.lon = None
        self.ele = None
        self.azi = None
        self.roll = None
        self.pitch = None

        self.__getAttributes()



    def getTime(self):
        """
        Loads the time steps over the desired timeframe from all netCDF-files and returns them as one array.

        Returns:
            A numpy array containing datetime.datetime objects

        Example:
            Getting the time-stamps from an an already initiated Windlidar object 'lidar':

            >>> lidar.getTime()
        """

        time = self._getArrayFromNc('time')

        time = tools.num2time(time)  # converting seconds since 1970 to datetime objects
        time = self._local2UTC(time)


        return time

    def getRange(self):
        """
        Loads the range-gates from the netCDF-file which contains the last entries of the desired timeframe.
        Note: just containing the range-gates from the first valid file of all used netCDF-files. If the range-gating
        changes over the input-timewindow, then you might run into issues.

        Returns:
            A numpy array with height in meters

        Example:
            Getting the range-gates of an already initiated Windlidar object called 'lidar':

            >>> lidar.getRange()
        """

        range = self._getArrayFromNc("range")

        # in case of many days being loaded and their range might be concatenated they will be split here:
        range = range[:np.nanargmax(range)+1]


        return range

    def getIntensity(self, version="alpha"):
        """
        Loads the volume attenuated backwards scattering from the "volume attenuated backwarts scattering function in
        air".

        Args:
            version: can be either "alpha" or "beta"

        Returns:
            A numpy array with the backscatter Intensity
        """


        if version == "alpha":
            intensity = self._getArrayFromNc("intensity")
        elif version == "beta":
            intensity = self._getArrayFromNc("beta")
        else:
            print("Not a valid version: %s"%version)
            return None

        return intensity

    def getVelocity(self,version="corrected"):
        """
        The radial velocity of of scatterers away from the instrument.

        Args:
            version: can be either corrected or uncorrected

        Returns:
            A numpy array with the velocity.

        """
        if version == "uncorrected":
            vel = self._getArrayFromNc("dv")
        elif version == "corrected":
            vel = self._getArrayFromNc("dv_corr")
        else:
            print("Not a valid version: %s" % version)
            return None

        return vel

 
    def __getPath(self):
        """
        Reads the Path from the settings.ini file by calling the right function from Device_module.

        Returns: Path of the Windlidar data.

        """
        return getValueFromSettings("WINDLIDAR_PATH")



    def __getAttributes(self):
        """
        Function to load the static attributes from the netCDF file.
        """
        _date = self.start.date()
        _datestr = _date.strftime("%Y%m")
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime("%Y%m%d")
        # _file = glob.glob(self.path + _datestr + "/" +  _nameStr)[0]

        if BCO.USE_FTP_ACCESS:
            _file = self._ftp_files[0]
        else:
            _file = glob.glob(self.path + _nameStr)[0]

        if "bz2" in _file[-5:]:
            nc = tools.bz2Dataset(_file)
        else:
            nc = Dataset(_file)
        self.title = nc.title
        self.device = nc.devices
        self.systemID = nc.systemID
        self.scanType = nc.scanType
        self.focusRange = nc.focusRange
        self.temporalResolution = nc.resolution.split(";")[0]
        self.location = nc.location
        nc.close()

        self.lat = self._getValueFromNC("lat")
        self.lon = self._getValueFromNC("lon")
        self.pitch = self._getValueFromNC("pitch")
        self.azi = self._getValueFromNC("azi")
        self.ele = self._getValueFromNC("ele")
        self.roll = self._getValueFromNC("roll")






