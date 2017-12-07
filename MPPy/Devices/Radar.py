import sys
from datetime import datetime as dt
import datetime
from MPPy.Devices.Device_module import Device, getFilePath
import MPPy.tools.tools as tools
import glob
import numpy as np

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the MPPy-package to work.")
    sys.exit(1)


class Radar(Device):
    """



    """

    def __init__(self, start, end, device="CORAL", version=2):
        """
        Class for working with radar data from Barbados.  \n
        Currently supported devices: -CORAL     \n
                                     -KATRIN    \n

        :param start: start of the timeframe ( for more info run Radar.help() )
        :param end: end of the timeframe ( for more info run Radar.help() )
        :param device: the device you want to use. Currently supported: CORAL, KATRIN
        :param version: The version of the dataset to use. Currently supported: 1,2,3  [note: 3 is in beta-phase]
        """

        self.device = device
        self.pathFlag = self.__getFlag()
        self.start = self.CheckInputTime(start)
        self.end = self.CheckInputTime(end)
        self.data_version = version
        self.path = self.__getPath()
        self.__checkInput()

    def __str__(self):
        returnStr = "%s Radar.\nUsed data version %i.\nLoad data from %s to %s." % \
                    (self.device, self.data_version, self.start, self.end)
        return returnStr

    def __checkInput(self):
        """
        This funcion checks for mistakes made by the user.  \n
        1. Check if device is supported \n
        2. Check if data-version is supported   \n
        3. Check if device was running on desired timeframe
        """

        if self.device != "CORAL" and self.device != "KATRIN":
            print("The only devices allowed are CORAL and KATRIN.\n%s is not a valid device!" % device)
            sys.exit(1)

        _versions_avail = [1, 2, 3]
        if not self.data_version in _versions_avail:
            print(
                "The version of the Dataset needs to be between %i and %i" % (_versions_avail[0], _versions_avail[-1]))
            sys.exit(1)

        try:  # check if device was running on selected timeframe
            for _date in tools.daterange(self.start, self.end):
                _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
                _file = glob.glob(self.path + _nameStr)[0]
        except:
            print("The Device %s was not running on %s. Please adjust timeframe.\n" \
                  "For more information about device uptimes visit\n" \
                  "http://bcoweb.mpimet.mpg.de/systems/data_availability/DeviceAvailability.html" % (
                  self.device, _date))
            sys.exit(1)

    def __getFlag(self):
        """
        Sets the flag which is used in the datapath to determine the device.  \n
        This can either be "MBR" for the CORAL or "KATRIN" for KATRIN
        """

        if self.device == "CORAL":
            return "MBR"
        elif self.device == "KATRIN":
            return "KATRIN"

    def getReflectivity(self):
        """
        Loads the reflecitivity over the desired timeframe from multiple netCDF-files and returns them as one array.
        :return: 2-D numpy array with getReflectivity in dbz
        """
        dbz_list = []
        for _date in tools.daterange(self.start, self.end):
            _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
            _file = glob.glob(self.path + _nameStr)[0]

            nc = Dataset(_file, mode="r")
            dbzFromDate = nc.variables["Zf"][:].copy()
            dbz_list.append(dbzFromDate)
            nc.close()

        dbz = dbz_list[0]
        if len(dbz_list) > 1:
            for item in dbz_list:
                dbz = np.concatenate((dbz, item))

        return dbz

    def getTime(self):
        """
        Loads the getTime steps over the desired timeframe from all netCDF-files and returns them as one array.
        :return: numpy array containing datetime.datetime objects
        """
        time_list = []
        for _date in tools.daterange(self.start, self.end):
            _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
            _file = glob.glob(self.path + _nameStr)[0]

            nc = Dataset(_file, mode="r")
            timeFromDate = nc.variables["time"][:].copy()
            time_list.append(timeFromDate)
            nc.close()

        time = time_list[0]
        if len(time_list) > 1:
            for item in time_list:
                time = np.concatenate((time, item))

        time = tools.num2time(time)  # converting seconds since 1970 to datetime objects
        return time

    def getRange(self):
        """
        Loads the getRange-gates from the netCDF-file which contains the last entries of the desired timeframe.
        :return: numpy array with height in meters
        """
        for _date in tools.daterange(self.start, self.end):
            continue

        _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
        _file = glob.glob(self.path + _nameStr)[0]
        nc = Dataset(_file, mode="r")
        range = nc.variables["range"][:].copy()

        return range

    def __getPath(self):
        __versionStr = "Version_%i" % self.data_version
        PATH = "%s%s/" % (getFilePath("RADAR"), __versionStr)
        print(PATH)
        return PATH

    def keys(self):
        __keys = ['getReflectivity', 'getTime', 'getRange']
        return __keys

    def help(self):
        print("This class provides acces to the radar data from the Max-Planck-Institute owned radars on Barbados.\n")
        print("Input for start and end can either be a datetime-object or a string.\n" \
              "If it is a string the it needs to have the format YYYYMMDDhhmmss, where\n" \
              "Y:Year, M:Month, D:Day, h:Hour, m:Minute, s:Second.\n" \
              "Missing steps will be appended automatically with the lowest possible value. Example:\n" \
              "input='2017' -> '20170101000000'.")
