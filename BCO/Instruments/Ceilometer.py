"""
This Module contains the Ceilometer class. This class is for easy working with the cloud base height.
"""

import sys
import bz2
import glob
import numpy as np
from datetime import timedelta
import fnmatch

import BCO.tools.convert
from BCO.tools import tools
from BCO.Instruments.Device_module import __Device
import BCO


try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)


class Ceilometer(__Device):
    """
    The ceilometer is an instrument for detecting the cloud base height (CBH).

    Args:
        start: Either String or datetime.datetime-object indicating the start of the timewindow
        end: Either String or datetime.datetime-object indicating the end of the timewindow

    Attributes:
        title: Short description of the data.
        location: Latitude and Longitude.
        rain_info: Description of the rain flag.
        cbh_info: Description of the different methods for deriving the CBH.
        resolution: temporal and vertical Resolution.
        instrument: Short description of the instrument.

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
        self._name_str = BCO.config[self._instrument]["NAME_SCHEME"]
        self._path_addition = BCO.config[self._instrument]["PATH_ADDITION"]
        self._path_addition = None if self._path_addition == "None" else self._path_addition # convert str to None
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
        for _date in tools.daterange(self.start.date(), self.end.date(), step="month"):
            if not self._path_addition:
                _nameStr = tools.getFileName(self._instrument, _date, use_ftp=BCO.USE_FTP_ACCESS,
                                             filelist=self._ftp_files).split("/")[-1]
            else:
                _nameStr = "/".join(tools.getFileName(self._instrument, _date, use_ftp=BCO.USE_FTP_ACCESS,
                                                      filelist=self._ftp_files).split("/")[-2:])

            if BCO.USE_FTP_ACCESS:
                for _f in self._ftp_files:
                    if fnmatch.fnmatch(_f,"*"+_nameStr.split("/")[-1]):
                        _file = _f
                        break
            else:
                _file = glob.glob(self.path + _nameStr)[0]

            nc = self._getNc(_date)

            # print(_date)
            _start, _end = self._getStartEnd(_date, nc)
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


    def _getStartEnd(self, _date, nc):
        """
        Find the index of the start-date and end-date argument in the netCDF-file. If the time-stamp is not in the
        actual netCDF-file then return the beginning and end of that file.
        Args:
            _date: datetime.datetime-object to compare self.start and self.end with.
            nc: the netCDF-Dataset

        Returns:
            _start: index of the _date in the actual netCDF-file. If not index in the netCDF-file then return 0
                    (beginning of the file)
            _end: index of the _date in the actual netCDF-file. If not index in the netCDF-file then return -1
                    (end of the file)
        """
        # This method overrides the standard method in device_module, because data is stored monthly and not daily

        _start = 0
        _end = 0
        if _date.month == self.start.month:
            _start = np.argmin(np.abs(np.subtract(nc.variables["time"][:], BCO.tools.convert.time2num(self.start, utc=False))))
            # print("start", _start)
        if _date.month == self.end.month:
            _end = np.argmin(np.abs(np.subtract(nc.variables["time"][:], BCO.tools.convert.time2num(self.end + timedelta(days=1), utc=False))))
            # print("end ", _end)

        return _start, _end


    def getTime(self):
        """
        Loads the time steps over the desired timeframe from all netCDF-files and returns them as one array.

        Returns:
            A numpy array containing datetime.datetime objects

        Example:
            Getting the time-stamps from an an already initiated Radiation object 'rad':

            >>> rad.getTime()
        """

        time = self._getArrayFromNc('time')

        time = BCO.tools.convert.num2time(time)  # converting seconds since 1970 to datetime objects

        return time

    def getCBH(self,method="cbh"):
        """
        This method retrieves the cloud base height (CBH) from the ceilometer data.
        Three different cloud base heights are included, derived using different methods:

        The first method detects a cbh as the lowest of two consecutive heights at which the smoothed backscattered
        signal (smoothed using a sliding average over 180 m) exceeds the average of the unsmoothed backscattered signal
        (in # of photons) plus a standarderror (the squared root of # of photons) of a 60 m window below it:
        a height-and-time dependent threshold (cbh). (Default)

        The second method defines the first cloud base height (chb_2s) as the height at which the unsmoothed
        backscatter signal in 2 consecutive range bins of 15 m exceeds the average backscatter of that profile plus
        2 times its standard deviation: a time-dependent threshold.

        The third method simply reads the cloud base height estimates provided by the instrument
        software (jenoptik).

        Args:
            method: one of: [cbh], cbh_2s, jenoptik

        Returns:
            Numpy array containing the CBH.
        """

        methods = {"cbh":"cbh_1",
                   "cbh_2s":"cbh_2s_1",
                   "jenoptik":"cbh_jenoptik_1"}

        if not method in methods:
            print("method must be one of: %s"%",".join(methods))
            print(self.cbh_info)

        cbh = np.asarray(self._getArrayFromNc(methods[method]))
        cbh[np.where(cbh < -990)] = np.nan
        return cbh


    def getRainFlag(self):
        """
        The values can be either 0 or 1.

            0 = No Rain
            1 = Rain

        Returns:
            Numpy array containing the rain flag.
        """

        rf = self._getArrayFromNc("flag_rain").astype(float)
        rf[np.where(rf < -990)] = np.nan
        return rf

    def getInstrumentStatusFlag(self):
        """
        This method provides information on the status of the Instrument:

            0 = Instrument down
            1 = Instrument up and running

        Returns:
            Numpy array containing the status flag.
        """

        status = self._getArrayFromNc("flag_ceilo_status").astype(float)
        status[np.where(status < -990)] = np.nan
        return status

    def getJenoptikOutputFlag(self):
        """
        Status of standard Jenoptik output files.

            0 = Absent
            1 = Present

        Returns:
            Numpy array containing the status flag.
        """

        status = self._getArrayFromNc("flag_jenoptik_output").astype(float)
        status[np.where(status < -990)] = np.nan
        return status


    def getMRRStatusFlag(self):
        """
        MRR operational status.

            0 = Down
            1 = Up and running

        Returns:
            Numpy array containing the status flag.
        """

        status = self._getArrayFromNc("flag_mrr_status").astype(float)
        status[np.where(status < -990)] = np.nan
        return status