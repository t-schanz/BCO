import sys
import datetime
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import bz2
import os
from pytz import timezone,utc

from BCO.tools import tools

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)


class __Device(object):
    """
    This class provide some general functions to work with. Many of the instrument classes will inherit from this
    calass.

    """

    de_tz = timezone("Europe/Berlin")
    utc_tz = timezone("UTC")

    def _checkInputTime(self, input):
        """
        Checking input for the right dataformat. This can either be a string, then it will be converted to a
        datetime-object, or it already is a datetime-obj, then it will just be passed.

        Args:
            input: str, or datetime.datetime

        Returns:
            datetime.datetime object
        """

        def _raiseError(_in):
            """
            This is some kind of error to be raised. If any input is wrong this will tell what is wrond.

            Args:
                _in: The wrong input by the user.

            """
            print("Input for start and end can either be a datetime-object or a string.\n" 
                  "If it is a string the it needs to have the format YYYYMMDDhhmmss, where\n" 
                  "Y:Year, M:Month, D:Day, h:Hour, m:Minute, s:Second.\n" 
                  "Missing steps will be appended automatically with the lowest possible value. Example:\n" 
                  "input='2017' -> '20170101000000'.")

            print("{} is not a valid format for start or end input.".format(_in))
            sys.exit(1)

        _input = input
        if type(_input) == str:

            def __repeat_to_length(string_to_expand, length):
                while len(string_to_expand) < length:
                    while len(string_to_expand) < 8:
                        string_to_expand += "01"
                    string_to_expand += "0"
                return string_to_expand

            _input = __repeat_to_length(_input, 14)
            try:
                _timeObj = dt(int(_input[:4]), int(_input[4:6]), int(_input[6:8]),
                              int(_input[8:10]), int(_input[10:12]), int(_input[12:14]))
            except:
                _raiseError(_input)

        elif type(_input) == datetime.datetime:
            _timeObj = _input

        else:
            _raiseError(_input)

        return _timeObj

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

        _start = 0
        _end = 0
        if _date == self.start.date():
            _start = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.start))))
            # print("start", _start)
        if _date == self.end.date():
            _end = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.end))))
            # print("end ", _end)

        return _start, _end

    def _FileNotAvail(self, skipped):
        print("For the following days of the chosen timewindow no files exists:")
        for element in skipped:
            print(element)
        self.skipped = skipped

    def _local2UTC(self, time):
        f1 = lambda x : x.astimezone(self.de_tz).astimezone(utc)
        return np.asarray(list(map(f1, time)))





def getValueFromSettings(device: str):
    """
    This function gets a value from the settings.ini and returns it:

    Args:
        device: Straing of the Device of which you want to get the data-path to the netCDF-file from.

    Returns:
        String of the value which is written in the file settings.ini behind the ':'. Only the string having the 'device'
        somewhere in the line will be returned.

    """
    package_directory = os.path.dirname(os.path.abspath(__file__))
    ini_file = package_directory + "/settings.ini"
    with open(ini_file, "r") as f:
        while True:
            try:
                line = f.readline().rstrip()
                if device + ":" in line:
                    return line.split(":")[1]
            except:
                break
