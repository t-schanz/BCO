import sys
import datetime
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
import os
from pytz import timezone,utc
from ftplib import FTP

import BCO.tools.convert
from BCO.tools import tools
import BCO
import glob
import tempfile
import re
import fnmatch
import configparser
from six import reraise as raise_
from future.utils import raise_from

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)


class __Device(object):
    """
    This class provide some general functions to work with. Many of the instrument classes will inherit from this
    class.

    """

    __de_tz = timezone("Europe/Berlin")
    __utc_tz = timezone("UTC")


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
        if isinstance(_input,str):

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

        elif isinstance(_input, datetime.datetime):
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
            _start = np.argmin(np.abs(np.subtract(nc.variables["time"][:], BCO.tools.convert.time2num(self.start, utc=True))))
            # print("start", _start)
        if _date == self.end.date():
            _end = np.argmin(np.abs(np.subtract(nc.variables["time"][:], BCO.tools.convert.time2num(self.end, utc=True))))
            # print("end ", _end)

        return _start, _end


    def _FileNotAvail(self, skipped):
        print("For the following days of the chosen timewindow no files exists:")
        for element in skipped:
            print(element)
        self.skipped = skipped


    def _local2UTC(self, time):
        if sys.version_info >= (3,6):
            f1 = lambda x : x.astimezone(self.__de_tz).astimezone(utc)
            return np.asarray(list(map(f1, time)))
        else:
            f1 = lambda x: self.__de_tz.localize(x).replace(tzinfo=self.__utc_tz)
            return np.asarray(list(map(f1, time)))

    def _downloadFromFTP(self,file,ftp_client=None):
        """
        Downloads the file from the mpi-zmaw server and saves it on the local machine.

        Args:
            file: Filename and path as listed on the FTP-server. Allowed to contain Wildcards.

        Returns:
            Path to the local directory of the downloaded file.
        """

        tmpdir = tempfile.gettempdir()

        _close_ftp_client = False
        if ftp_client == None:
            ftp_client = FTP(BCO.FTP_SERVER)
            ftp_client.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)
            _close_ftp_client = True
        # print(ftp_path + file)
        file_to_retrieve = ftp_client.nlst(file)[0]
        try:
            __save_file = os.path.split(file_to_retrieve)[-1]
        except:
            __save_file = file_to_retrieve

        if not os.path.isfile(os.path.join(tmpdir, __save_file)): # check if the file is already there:
            print("Downloading %s"%__save_file)
            ftp_client.retrbinary('RETR ' + file_to_retrieve, open(os.path.join(tmpdir, __save_file), 'wb').write)
        else:
            # print("File already in temporary folder: %s"%__save_file)
            pass
        self._ftp_files.append(os.path.join(tmpdir, __save_file))

        if _close_ftp_client:
            ftp_client.close()
        return tmpdir +"/"


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
        var_list = []
        skippedDates = []
        for _date in tools.daterange(self.start.date(), self.end.date()):
            _file = self._getFile(_date)

            try:
                nc = self._getNc(_date)

                # print(_date)
                _start, _end = self._getStartEnd(_date, nc)
                # print(_start,_end)
                if _end != 0:
                    varFromDate = nc.variables[value][_start:_end].copy()
                else:
                    varFromDate = nc.variables[value][_start:].copy()
                var_list.append(varFromDate)
                nc.close()

            except KeyError:
                nc.close()
                raise_


            except IOError as exc:
                raise_from(DatabaseError('failed to open'), exc)
                skippedDates.append(_date)
                continue




        _var = var_list[0]
        if len(var_list) > 1:
            for item in var_list[1:]:
                _var = np.concatenate((_var, item))

        if skippedDates:
            self._FileNotAvail(skippedDates)

        return _var


    def _getValueFromNc(self, value):
        """
        This function gets values from the netCDF-Dataset, which stay constant over the whole timeframe. So its very
        similar to _getArrayFromNc(), but without the looping.

        Args:
            value: A string for accessing the netCDF-file.
                    For example: 'Zf'

        Returns:
            Numpy array
        """
        _date = self.start.date()
        nc = self._getNc(_date)
        _var = nc.variables[value][:].copy()
        nc.close()

        return _var


    def _getAttrFromNC(self,value):

        """
        Get static attributes from the netcdf file.
        These are stored as plain text in the __str__ method of the netcdf-file

        Args:
            value: The attribute to retrieve.

        Returns:
            String of the Attribute.
        """

        _date = self.start.date()
        nc = self._getNc(_date)

        nc_lines = str(nc).split("\n")
        for line in nc_lines:
            if value in line:
                nc.close()
                return ":".join(line.split(":")[1:]).lstrip()


    def close(self):
        """
        Deletes all temporary stored files from the instance.

        Warnings:
            This method is only available when loading the data from the ftp server.
            It will not be available when working with the data directly inside the mpi / zmaw network (as it
            is not necessary there).

        """
        if BCO.USE_FTP_ACCESS:
            for file in self._ftp_files:
                os.remove(file)

            self._ftp_files = []
            print("Successfully deleted all temporary files")
        else:
            print("This method is just for use with ftp-access of the BCO Data")


    def _getPath(self):
        """
        Reads the Path from the settings.ini file by calling the right function from Device_module.

        Returns: Path of the data.

        """
        if BCO.USE_FTP_ACCESS:
            ftp_client = tools.getFTPClient(user=BCO.FTP_USER,passwd=BCO.FTP_PASSWD)
            for _date in tools.daterange(self.start.date(), self.end.date()):
                tmp_file = tools.getFileName(self._instrument,_date,use_ftp=BCO.USE_FTP_ACCESS,ftp_client=ftp_client)
                __path = self._downloadFromFTP(file=tmp_file,ftp_client=ftp_client)

            ftp_client.close()
            return __path

        else:
            tmp_path =  BCO.config[self._instrument]["PATH"]
            return tmp_path


    def _getFile(self,date):

        if not self._path_addition:
            _nameStr = tools.getFileName(self._instrument, date, use_ftp=BCO.USE_FTP_ACCESS,filelist=self._ftp_files).split("/")[-1]
        else:
            # print(self._instrument, date)
            _nameStr = "/".join(tools.getFileName(self._instrument, date, use_ftp=BCO.USE_FTP_ACCESS,filelist=self._ftp_files).split("/")[-2:])

        if BCO.USE_FTP_ACCESS:
            for _f in self._ftp_files:
                if fnmatch.fnmatch(_f, "*" + _nameStr.split("/")[-1]):
                    _file = _f
                    break
        else:
            _file = glob.glob(os.path.join(self.path, _nameStr))[0]

        return _file


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
        time = self._local2UTC(time)

        return time

    def __str__(self):
        callables = {"Methods": [func+"()" for func in dir(self) if callable(getattr(self, func)) and func[0] is not "_"],
                     "Attributes": [attr for attr in dir(self) if
                                    not callable(getattr(self, attr)) and attr[0] is not "_"]
                     }
        a0 = "==================================================\n"
        a1 = "Instrument : %s\n"%self._instrument
        a2 = "Timespan   : %s to %s\n"%(self.start.strftime("%x"), self.end.strftime("%x"))
        a3 = "Timesteps  : %s\n"%(len(self.getTime()))
        a4 = "Files from : %s\n"%self.path
        a5 = "--------------------------------------------------\n"
        a6 = "Methods    : %s\n"%"\n             ".join(callables["Methods"])
        a7 = "Attributes : %s\n"%"\n             ".join(callables["Attributes"])
        a8 = "=================================================="

        a_radar = None
        if "data_version" in locals():
            a9 = "Data version : %i"%int(self.data_version)
            to_print = [a0,a1,a2,a3,a9,a4,a5,a6,a7,a8]
        else:

            to_print = [a0,a1,a2,a3,a4,a5,a6,a7,a8]
        return "".join(to_print)




    def _getNc(self,date):
        """
        Only for development.

        Returns:
            Instance of open Dataset from nc-file.

        """
        _file = self._getFile(date)

        if "bz2" in _file[-5:]:
            nc = tools.bz2Dataset(_file)
        else:
            nc = Dataset(_file)

        return nc
