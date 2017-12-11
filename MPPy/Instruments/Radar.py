import sys
from datetime import datetime as dt
import datetime
from MPPy.Instruments.Device_module import __Device, getFilePath
import MPPy.tools.tools as tools
import glob
import numpy as np

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the MPPy-package to work.")
    sys.exit(1)


class Radar(__Device):
    """
    Class for working with radar data from Barbados.  \n
    Currently supported devices: CORAL, KATRIN     \n

    Args:
            start: Either String or datetime.datetime-object indicating the start of the timefwindow
            end: Either String or datetime.datetime-object indicating the end of the timefwindow
            device: the device you want to use. Currently supported: CORAL, KATRIN
            version: The version of the dataset to use. Currently supported: 1,2,3  [note: 3 is in beta-phase]

    Example:
        The following example initiates a radar object for the CORAL with a timewindow form the 1st January 2017 to
        the 2nd January 2017 to 3:30 pm:

        >>> coral = Radar(start="20170101",end="201701021530", device="CORAL")

        To get attributes of the device you just need to call the attribute now:

        >>> coral.lat
        array(13.162699699401855, dtype=float32)

        To get measured values you need to call the appropriate function:

        >>> coral.getReflectivity(postprocessing="Zf")
        array([[...]], dtype=float32)

        In most cases you want the timestamp as well:

        >>> coral.getTime()
        array([datetime.datetime(2017, 1, 1, 1, 0, 18), ...,
        datetime.datetime(2017, 1, 2, 0, 59, 49)], dtype=object)


    Attributes:
        device: String of the device being used. ('CORAL' or 'KATRIN')
        start: datetime.datetime object indicating the beginning of the chosen timewindow.
        end: datetime.datetime object indicating the end of the chosen timewindow.
        data_version: An Integer conatining the used version of the data (1,2,3[beta]) .
        lat: Latitude of the instrument.
        lon: Longitude of the instrument.
        azimuth: Azimuth angle of where the instrument is pointing to.
        elevation: Elevation angle of where the instrument is pointing to.
        north: Degrees of where from the instrument seen is north.
    """

    def __init__(self, start, end, device="CORAL", version=2):
        """
        Args:
            start: start of the timeframe ( for more info run Radar.help() )
            end: end of the timeframe ( for more info run Radar.help() )
            device: the device you want to use. Currently supported: CORAL, KATRIN
            version: The version of the dataset to use. Currently supported: 1,2,3  [note: 3 is in beta-phase]
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
        _end = -1
        if _date == self.start.date():
            _start = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.start))))
            print("start", _start)
        if _date == self.end.date():
            _end = np.argmin(np.abs(np.subtract(nc.variables["time"][:], tools.time2num(self.end))))
            print("end ", _end)

        return _start, _end

    def getReflectivity(self, postprocessing="Zf"):
        """
        Loads the reflecitivity over the desired timeframe from multiple netCDF-files and returns them as one array.

        Args:
            postprocessing: see Radar.help() for more inforamation

        Returns:
            2-D numpy array with getReflectivity in dbz

        Example:
            Getting the unfiltered and mie corrected reflectivity of all hydrometeors with an an already
            initiated radar object 'coral':

            >>> coral.getReflectivity(postprocessing="Zu")
        """

        if postprocessing in self.__getPostProcessingForVersion():
            dbz = self.__getArrayFromNc(value=postprocessing)
            return dbz
        else:
            print("ERROR: %s is not a valid postprocessing operator for data version %i." %
                  (postprocessing, self.data_version))
            print("Allowed operators are: %s" % (",".join(self.__getPostProcessingForVersion())))
            return None

    def getVelocity(self, target="hydrometeors"):
        """
        Loads the doppler velocity from the netCDF-files and returns them as one array

        Args:
            target: String of which target the velocity you want to get from: 'hydrometeors' or 'all'.

        Returns:
            2-D numpy array with doppler velocity in m/s

        Example:
            This is how you could get the velocity from all targets for the 13th August 2016 to the 15th August 2016
            of CORAL:

            >>> coral = Radar(start="20160813",end="20160815", device="CORAL")
            >>> velocity = Radar.getVelocity(target="all")
        """

        targets = ["hydrometeors", "all"]
        if target in targets:
            if target == "all":
                key = "VELg"
            else:
                key = "VEL"

            velocity = self.__getArrayFromNc(key)
            return velocity
        else:
            print("%s is not a valid target." % target)
            print("Allowed targets are: %s" % ", ".join(targets))
            return None

    def getTime(self):
        """
        Loads the time steps over the desired timeframe from all netCDF-files and returns them as one array.

        Returns:
            A numpy array containing datetime.datetime objects

        Example:
            Getting the time-stamps from an an already initiated radar object 'coral':

            >>> coral.getTime()
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
            for i, item in enumerate(time_list):
                time = np.concatenate((time, item))
                del time_list[i]
        time = tools.num2time(time)  # converting seconds since 1970 to datetime objects
        return time

    def getRange(self):
        """
        Loads the getRange-gates from the netCDF-file which contains the last entries of the desired timeframe.
        Note: just containing the range-gates from the last file of all used netCDF-files. If the range-gating canges
        over the input-timewindow, then you might run into issues.

        Returns:
            A numpy array with height in meters

        Example:
            Getting the range-gates of an already initiated radar object called 'coral':

            >>> coral.getRange()
        """
        for _date in tools.daterange(self.start, self.end):
            continue

        _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
        _file = glob.glob(self.path + _nameStr)[0]
        nc = Dataset(_file, mode="r")
        range = nc.variables["range"][:].copy()

        return range

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
            >>> _var = nc.variables[value][self.start:self.end].copy()

            Just that in this function we are looping over all files and in the end concatinating them.
        """

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
            for i, item in enumerate(var_list):
                _var = np.concatenate((_var, item))
                del var_list[i]  # for more efficiency when handling large amounts of data

        return _var

    def __getValueFromNc(self, value:str):
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
        _nameStr = "MMCR__%s__Spectral_Moments*%s.nc" % (self.pathFlag, tools.datestr(_date))
        _file = glob.glob(self.path + _nameStr)[0]
        nc = Dataset(_file, mode="r")
        _var = nc.variables[value][:].copy()
        nc.close()
        return _var

    def __getPostProcessingForVersion(self):
        """
        Function for reading the valid reflectivity values from the initiation file.

        Returns:
            List of valid reflectivity-postprocessing strings, for example:
            ["Zf","Ze","Zu"]
        """

        _vars = getFilePath("RADAR_VERSION_%i_REFLECTIVITY_VARIABLES" % self.data_version).split(",")
        return _vars

    def __getPath(self):
        __versionStr = "Version_%i" % self.data_version
        PATH = "%s%s/" % (getFilePath("RADAR"), __versionStr)
        print(PATH)
        return PATH

    # @staticmethod
    # def keys():
    #     __keys = ['getReflectivity', 'getTime', 'getRange']
    #     return __keys

    @staticmethod
    def help():
        """
        This is a function for less experienced python-users. It will print some tipps for working with this Radar
        class. If possible use the documentation, it will be much more likely up to date and contains more information!

        Returns:
            Just prints some help messages into the console
        """

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

        print("Please have a look at the documentation. It contains examples for many usecases.\n"
              "www.hereWillBeTheDocumentationAtSomePoint.de \n"
              "at the moment: docs/_build/html/index.html")
