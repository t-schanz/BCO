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

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
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

        self.start = self.checkInputTime(start) + timedelta(hours=0)
        self.end = self.checkInputTime(end) + timedelta(hours=0)
        self.path = self.__getPath()
        print(self.path)

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

        time = self.__getArrayFromNc('time')

        time = tools.num2time(time)  # converting seconds since 1970 to datetime objects
        time = self.local2UTC(time)


        return time

    @staticmethod
    def __removeTimeOffset(time):
        return time - timedelta(hours=1)

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

        range = None
        for _date in tools.daterange(self.start, self.end):
            if not range:
                try:
                    _datestr = _date.strftime("%Y%m")
                    _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime(
                        "%Y%m%d")
                    # _file = glob.glob(self.path + _datestr + "/" + _nameStr)[0]
                    _file = glob.glob(self.path + _nameStr)[0]

                    if "bz2" in _file[-5:]:
                        nc = tools.bz2Dataset(_file)
                    else:
                        nc = Dataset(_file)

                    range = nc.variables["range"][:].copy()
                    return range
                except:
                    continue

        return None

    def getIntensity(self):
        """
        Loads the volume attenuated backwards scattering from the "volume attenuated backwarts scattering function in
        air".

        Returns:
            A numpy array with the backscatter Intensity
        """


        intensity = self.__getArrayFromNc("intensity")
        return intensity

    def getVelocity(self):
        """
        The radial velocity of of scatterers away from the instrument.

        Returns:
            A numpy array with the velocity.

        """
        vel = self.__getArrayFromNc("dv")
        return vel

    def __getArrayFromNc(self, value):
        """
        Retrieving the 'value' from the netCDF-Dataset reading just the desired timeframe.

        Args:
            value: String which is a valid key for the Dataset.variables[key].

        Returns:
            Numpy array with the values of the desired key and the inititated time-window.

        Example:
            What behind the scenes happens for an example-key 'VEL' is something like:

            >>> nc = Dataset(input_file)
            >>> _var = nc.variables["VEL"][self.start:self.end].copy()

            Just that in this function we are looping over all files and in the end concatinating them.
        """
        var_list = []
        skippedDates = []
        for _date in tools.daterange(self.start.date(), self.end.date()):
            _datestr = _date.strftime("%Y%m")
            _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime("%Y%m%d")
            # _file = glob.glob(self.path + _datestr + "/" + _nameStr)[0]
            _file = glob.glob(self.path + _nameStr)[0]
            try:
                if "bz2" in _file[-5:]:
                    nc = tools.bz2Dataset(_file)
                else:
                    nc = Dataset(_file)

                # print(_date)
                _start, _end = self.getStartEnd(_date, nc)
                # print(_start,_end)
                if _end != 0:
                    varFromDate = nc.variables[value][_start:_end].copy()
                else:
                    varFromDate = nc.variables[value][_start:].copy()
                var_list.append(varFromDate)
                nc.close()
            except:
                skippedDates.append(_date)
                continue

        _var = var_list[0]
        if len(var_list) > 1:
            for item in var_list[1:]:
                _var = np.concatenate((_var, item))

        if skippedDates:
            self.FileNotAvail(skippedDates)

        return _var

    def __getPath(self):
        """
        Reads the Path from the settings.ini file by calling the right function from Device_module.

        Returns: Path of the Windlidar data.

        """
        return getValueFromSettings("WINDLIDAR_PATH")

    def get_nc(self):
        for _date in tools.daterange(self.start.date(), self.end.date()):
            _datestr = _date.strftime("%Y%m")
            _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime("%Y%m%d")
            # _file = glob.glob(self.path + _datestr + "/" + _nameStr)[0]
            _file = glob.glob(self.path + _nameStr)[0]
            if "bz2" in _file[-5:]:
                nc = tools.bz2Dataset(_file)
            else:
                nc = Dataset(_file)
        return nc

    def __getAttributes(self):
        """
        Function to load the static attributes from the netCDF file.
        """
        _date = self.start.date()
        _datestr = _date.strftime("%Y%m")
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime("%Y%m%d")
        # _file = glob.glob(self.path + _datestr + "/" +  _nameStr)[0]
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

        self.lat = self.__getValueFromNc("lat")
        self.lon = self.__getValueFromNc("lon")
        self.pitch = self.__getValueFromNc("pitch")
        self.azi = self.__getValueFromNc("azi")
        self.ele = self.__getValueFromNc("ele")
        self.roll = self.__getValueFromNc("roll")


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
        _nameStr = "WindLidar__Deebles_Point__VerticalVelocity__STARE__1s__%s.nc*" % _date.strftime("%Y%m%d")
        # _file = glob.glob(self.path + _datestr + "/" +  _nameStr)[0]
        _file = glob.glob(self.path + _nameStr)[0]

        if "bz2" in _file[-5:]:
            nc = tools.bz2Dataset(_file)
        else:
            nc = Dataset(_file)

        _var = nc.variables[value][:].copy()
        nc.close()

        return _var




