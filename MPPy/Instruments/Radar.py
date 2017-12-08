import sys
from datetime import datetime as dt
import datetime
from MPPy.Instruments.Device_module import Device, getFilePath
import MPPy.tools.tools as tools
import glob
import numpy as np

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the MPPy-package to work.")
    sys.exit(1)


class Radar(Device):
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

        self.lat = self.__getValueFromNc("lat")
        self.lon = self.__getValueFromNc("lon")
        self.azimuth = self.__getValueFromNc("azi")
        self.elevation = self.__getValueFromNc("elv")
        self.north = self.__getValueFromNc("north")


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
            print("The only devices allowed are CORAL and KATRIN.\n%s is not a valid device!" % self.device)
            sys.exit(1)

        _versions_avail = [1, 2, 3]
        if self.data_version not in _versions_avail:
            print(
                "The version of the Dataset needs to be between %i and %i" % (_versions_avail[0], _versions_avail[-1]))
            sys.exit(1)

        try:  # check if device was running on selected timeframe
            for _date in tools.daterange(self.start, self.end):
                _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
                _file = glob.glob(self.path + _nameStr)[0]
        except:
            print("The Device %s was not running on %s. Please adjust timeframe.\n" 
                  "For more information about device uptimes visit\n" 
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

    def __getStartEnd(self, _date, nc):
        _start = 0
        _end = -1
        if _date == self.start.date():
            _start = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.start))))
            print("start", _start)
        if _date == self.end.date():
            _end = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.end))))
            print("end ", _end)

        return _start, _end

    def getReflectivity(self,postprocessing="Zf"):
        """
        Loads the reflecitivity over the desired timeframe from multiple netCDF-files and returns them as one array.
        :param postprocessing: see Radar.help() for more inforamation
        :return: 2-D numpy array with getReflectivity in dbz
        """

        if postprocessing in self.__getPostProcessingForVersion():
            dbz = self.__getArrayFromNc(value=postprocessing)
            return dbz
        else:
            print("ERROR: %s is not a valid postprocessing operator for data version %i."%
                  (postprocessing,self.data_version))
            print("Allowed operators are: %s"%(",".join(self.__getPostProcessingForVersion())))
            return None


    def getVelocity(self,target="hydrometeors"):
        """
        Loads the doppler velocity from the netCDF-files and returns them as one array
        :param target:  'hydrometeors' or 'all'
        :return: 2-D numpy array with doppler velocity in m/s
        """
        targets = ["hydrometeors","all"]
        if target in targets:
            if target == "all":
                key = "VELg"
            else:
                key= "VEL"

            velocity = self.__getArrayFromNc(key)
            return velocity
        else:
            print("%s is not a valid target."%target)
            print("Allowed targets are: %s"%", ".join(targets))
            return None


    def getTime(self):
        """
        Loads the getTime steps over the desired timeframe from all netCDF-files and returns them as one array.
        :return: numpy array containing datetime.datetime objects
        """
        time_list = []
        for _date in tools.daterange(self.start.date(), self.end.date()):
            _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
            _file = glob.glob(self.path + _nameStr)[0]

            nc = Dataset(_file, mode="r")
            _start, _end = self.__getStartEnd(_date, nc)
            timeFromDate = nc.variables["time"][_start:_end].copy()
            time_list.append(timeFromDate)
            nc.close()

        time = time_list[0]
        if len(time_list) > 1:
            for i,item in enumerate(time_list):
                time = np.concatenate((time, item))
                del time_list[i]
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


    def __getArrayFromNc(self,value):
        var_list = []
        for _date in tools.daterange(self.start.date(), self.end.date()):
            _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
            _file = glob.glob(self.path + _nameStr)[0]
            nc = Dataset(_file, mode="r")
            # print(_date)
            _start, _end = self.__getStartEnd(_date, nc)
            varFromDate = nc.variables[value][_start:_end].copy()
            var_list.append(varFromDate)
            nc.close()

        _var = var_list[0]
        if len(var_list) > 1:
            for i,item in enumerate(var_list):
                _var = np.concatenate((_var, item))
                del var_list[i] # for more efficiency when handling large amounts of data

        return _var

    def __getValueFromNc(self,value):
        _date = self.start.date()
        _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
        _file = glob.glob(self.path + _nameStr)[0]
        nc = Dataset(_file, mode="r")
        _var= nc.variables[value][:].copy()
        nc.close()
        return _var

    def __getPostProcessingForVersion(self):
        _vars = getFilePath("RADAR_VERSION_%i_REFLECTIVITY_VARIABLES"%self.data_version).split(",")
        return _vars

    def __getPath(self):
        __versionStr = "Version_%i" % self.data_version
        PATH = "%s%s/" % (getFilePath("RADAR"), __versionStr)
        print(PATH)
        return PATH

    @staticmethod
    def keys():
        __keys = ['getReflectivity', 'getTime', 'getRange']
        return __keys

    @staticmethod
    def help():
        print("This class provides acces to the radar data from the Max-Planck-Institute owned radars on Barbados.\n")
        print("Input for start and end: can either be a datetime-object or a string.\n" 
              "   If it is a string the it needs to have the format YYYYMMDDhhmmss, where\n" 
              "   Y:Year, M:Month, D:Day, h:Hour, m:Minute, s:Second.\n" 
              "   Missing steps will be appended automatically with the lowest possible value. Example:\n" 
              "   input='2017' -> '20170101000000'.\n")
        print("Be careful with the timeframe as 1 month of data takes about 1GB of ram.\n")
        print("Input for Version: Can be one of 1,[2],3\n")
        print("reflectivity: can be called with parameter 'postprocessing'.\n"
              "   This can be one of [Zf],Ze,Zg,Zu.\n"
              "     Zf: Filtered and Mie corrected Radar Reflectivity of all Hydrometeors\n"
              "     Ze: Unfiltered Equivalent Radar Reflectivity of all Hydrometeors\n"
              "     Zu: Unfiltered and Mie corrected Radar Reflectivity of all Hydrometeors\n"
              "     Zg: Unfiltered Equivalent Radar Reflectivity of all Targets (global)\n"
              "   Note: not all parameters might be available for every data_version")

