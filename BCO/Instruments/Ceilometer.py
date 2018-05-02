"""
This Module contains the Ceilometer class. This class is for easy working with the cloud base height.
"""

import sys
import bz2
import glob
import numpy as np
from datetime import timedelta
import fnmatch


from BCO.tools import tools
from BCO.Instruments.Device_module import __Device,getValueFromSettings
import BCO


try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)


class Ceilometer(__Device):
    """


    """
    def __init__(self, start, end):
        """
        Sets up some variables and loads static parameters from the netcdf file.

        Args:
            start: start of the timeframe.
            end: end of the timeframe.
        """

        self.start = self._checkInputTime(start) + timedelta(hours=0)
        self.end = self._checkInputTime(end) + timedelta(hours=0)


        self._instrument = BCO.config["CEILOMETER"]["INSTRUMENT"] # String used for retrieving the filepath from settings.ini
        print(self._instrument)
        self._name_str = BCO.config[self._instrument]["NAME_SCHEME"]
        self._path_addition = BCO.config[self._instrument]["PATH_ADDITION"]
        self._path_addition = None if self._path_addition == "None" else self._path_addition # convert str to None
        print("Name Str: " + self._name_str)
        self._ftp_files = []
        self.path = self._getPath()

        # Attributes:
        self.title = None
        self.location = None
        self.rain_info = None
        self.cbh_info = None
        self.resolution = None
        self.instrument = None

        self.__getAttributes()

    def __getAttributes(self):
        """
        Function to load the static attributes from the netCDF file.
        """

        self.title = self._getAttrFromNC("title")
        self.location = self._getAttrFromNC("location")

        self.rain_info = self._getAttrFromNC("details_rain")
        self.cbh_info = self._getAttrFromNC("details_cbh")

        self.resolution = self._getAttrFromNC("resolution")
        self.instrument = self._getAttrFromNC("instrument")

    def _getArrayFromNc(self, value):
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
        # This method overrides the standard method in device_module, because data is stored monthly and not daily

        var_list = []
        skippedDates = []
        for _date in tools.daterange(self.start.date(), self.end.date()):
            if not self._path_addition:
                _nameStr = tools.getFileName(self._instrument, _date).split("/")[-1]
            else:
                _nameStr = "/".join(tools.getFileName(self._instrument, _date).split("/")[-2:])

            if BCO.USE_FTP_ACCESS:
                for _f in self._ftp_files:
                    if fnmatch.fnmatch(_f,"*"+_nameStr.split("/")[-1]):
                        _file = _f
                        break
            else:
                _file = glob.glob(self.path + _nameStr)[0]


            if "bz2" in _file[-5:]:
                nc = tools.bz2Dataset(_file)
                print("bz file")
            else:
                nc = Dataset(_file)

            # print(_date)
            _start, _end = self._getStartEnd(_date, nc)
            # print(_start,_end)
            if _end != 0:
                varFromDate = nc.variables[value][_start:_end].copy()
            else:
                varFromDate = nc.variables[value][_start:].copy()
            var_list.append(varFromDate)
            nc.close()



        _var = var_list[0]
        if len(var_list) > 1:
            for item in var_list[1:]:
                _var = np.concatenate((_var, item))

        if skippedDates:
            self._FileNotAvail(skippedDates)

        return _var