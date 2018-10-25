"""
This Module contains the Radar class. This class is for easy working with the BCO radar data.
"""

import sys
from datetime import datetime as dt
import datetime

import BCO.tools.convert
from BCO.Instruments.Device_module import __Device
import BCO.tools.tools as tools
import glob
import numpy as np
from pytz import timezone, utc
import BCO
import re

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)

__all__ = ['Radar']


class Radar(__Device):
    """
    Class for working with radar data from Barbados.  \n
    Currently supported devices: CORAL, KATRIN     \n

    Args:
            start: Either String or datetime.datetime-object indicating the start of the timewindow
            end: Either String or datetime.datetime-object indicating the end of the timewindow
            device: the device you want to use. Currently supported: CORAL, KATRIN
            version: The version of the dataset to use. Currently supported: 1,2,3  [note: 3 is in beta-phase]

    Example:
        The following example initiates a radar object for the CORAL with a timewindow form the 1st January 2017 to
        the 2nd January 2017 to 3:30 pm:

        >>> coral = Radar(start="20170101",end="201701021530", device="CORAL")

        To review the attributes of your class you can use:

        >>> print(coral)
        CORAL Radar.
        Used data version 2.
        Load data from 2017-01-01 00:00:00 to 2017-01-02 15:30:00.

        To get attributes of the device you just need to call the attribute now:

        >>> coral.lat
        array(13.162699699401855, dtype=float32)

        To get measured values you need to call the appropriate method:

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
            skipped: if loading longer timeseries, where days might be missing, you can find those missing timesteps here.
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
        self.start = self._checkInputTime(start)
        self.end = self._checkInputTime(end)
        self.data_version = version
        self._instrument = BCO.config[device]["INSTRUMENT"] # String used for retrieving the filepath from settings.ini
        # print(self._instrument)

        BCO.config[self._instrument]["DATA_VERSION"] = "Version_%i/"%self.data_version
        self._name_str = BCO.config[self._instrument]["NAME_SCHEME"]
        self._path_addition = BCO.config[self._instrument]["PATH_ADDITION"]
        self._path_addition = None if self._path_addition == "None" else self._path_addition # convert str to None
        self._ftp_files = []
        self.path = self._getPath()


        if not BCO.USE_FTP_ACCESS:
            self.path += "Version_%i/" % version
        self.__checkInput()

        self.lat = self._getValueFromNc("lat")
        self.lon = self._getValueFromNc("lon")
        self.azimuth = self._getValueFromNc("azi")
        self.elevation = self._getValueFromNc("elv")
        try:
            self.north = self._getValueFromNc("northangle")
        except:
            self.north = self._getValueFromNc("north")
        self.skipped = None

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
                _nameStr = tools.getFileName(self.device,_date,use_ftp=BCO.USE_FTP_ACCESS,filelist=self._ftp_files).split("/")[-1]
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
            dbz = self._getArrayFromNc(value=postprocessing)
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

        targets = {"hydrometeors": "VEL",
                   "all": "VELg"}

        if not target in targets:
            print("%s is not a valid target. Please use on of %s" % (target, ", ".join(targets.keys())))
            return None

        velocity = self._getArrayFromNc(targets[target])

        return velocity


    def getMeltHeight(self):
        """
        Loads the melting layer height from all netCDF-Files and returns them as one array.

        Returns:
            A numpy array containing the melting layer height in meters.

        """
        meltHeight = self._getArrayFromNc('MeltHei')
        return meltHeight

    def getRadarConstant(self):
        """
        Loads the radar constant from all netCDF-Files and returns them as one array.

        Returns:
            A numpy array containing the radar constant in mm^6/m^3 for each timestep.

        """

        radarConstant = self._getArrayFromNc('RadarConst')
        return radarConstant

    def getNoisePower(self, channel):
        """
        Loads the HSdiv Noise Power in DSP of the desired channel from all netCDF-Files returns them as one array.

        Args:
            channel: String: can be either "Co" or "Cross".

        Returns:
            2D-numpy array containing the HSdiv Noise Power in DSP for all heigts and timesteps.
        """

        channels = {"Co": "HSDco",
                    "Cross": "HSDcx"}
        if not channel in channels:
            print("%s is not a valid channel. Please use on of %s" % (channel, ", ".join(channels.keys())))
            return None

        noise = self._getArrayFromNc(channels[channel])

        return noise

    def getLDR(self, target="hydrometeors"):
        """
        Loads the linear depolarization ratio (LDR) in dbZ of the desired target from all netCDF-Files returns them as one
         array. Allowed targets are: "hydrometeors" or "all". The default is "hydrometeors".

        Args:
            target: String: can be either "hydrometeors" or "all"

        Returns:
            2D-numpy array containing LDR in dbZ for all heigts and timesteps.

        """

        targets = {"hydrometeors": "LDR",
                   "all": "LDRg"}

        if not target in targets:
            print("%s is not a valid target. Please use on of %s" % (target, ", ".join(targets.keys())))
            return None

        ldr = self._getArrayFromNc(targets[target])

        return ldr

    def getRMS(self, target="hydrometeors"):
        """
        Loads the Peak Width RMS in m/s of the desired target from all netCDF-Files returns them as one
         array. Allowed targets are: "hydrometeors" or "all". The default is "hydrometeors".

        Args:
            target: String: can be either "hydrometeors" or "all"

        Returns:
            2D-numpy array containing LDR in m/s for all heigts and timesteps.

        """

        targets = {"hydrometeors": "RMS",
                   "all": "RMSg"}

        if not target in targets:
            print("%s is not a valid target. Please use on of %s" % (target, ", ".join(targets.keys())))
            return None

        rms = self._getArrayFromNc(targets[target])

        return rms

    def getSNR(self, target="hydrometeors"):
        """
        Loads the reflectivity SNR in dbZ of the desired target from all netCDF-Files and returns them as one
         array. Allowed targets are: "hydrometeors", "all" or "plank". The default is "hydrometeors".

        Args:
            target: String: can be either "hydrometeors","plank" or "all"

        Returns:
            2D-numpy array containing LDR in dbZ for all heigts and timesteps.

        """

        targets = {"hydrometeors": "SNRg",
                   "all": "SNR",
                   "plank": "SNRplank"}

        if not target in targets:
            print("%s is not a valid target. Please use on of %s" % (target, ", ".join(targets.keys())))
            return None

        snr = self._getArrayFromNc(targets[target])

        return snr

    def getRange(self):
        """
        Loads the range-gates from the netCDF-file which contains the last entries of the desired timeframe.
        Note: just containing the range-gates from the first valid file of all used netCDF-files. If the range-gating
        changes over the input-timewindow, then you might run into issues.

        Returns:
            A numpy array with height in meters

        Example:
            Getting the range-gates of an already initiated radar object called 'coral':

            >>> coral.getRange()
        """

        range = self._getArrayFromNc("range")

        # in case of many days being loaded and their range might be concatenated they will be split here:
        range = range[:np.nanargmax(range)+1]

        return range

    def getTransmitPower(self):
        """
         Loads the average transmit power in Watt of the desired target from all netCDF-Files returns them as one array.

        Returns:
            2D-numpy array containing average transmit power for all heigts and timesteps in W.
        """

        tpow = self._getArrayFromNc("tpow")

        return tpow

    def quickplot2D(self, value, save_name=None, save_path=None, ylim=None):
        """
        Creates a fast Quickplot from the input value. Start and end date are the initialization-dates. To save the
        picture you can provide a name for the picture (save_name). If no savepath is provided, the picture will be
        stored in the current working directory.

        Args:
            value: A 2-D array which you want to plot.
            save_name: String: If provided picture will be saved under the given name. Example: 'quicklook.png'
            save_path: String: If provided, the picture will be saved at this location. Example: '/user/hoe/testuer/'
            ylim: Tuple: If provided the y-axis will be limited to these values.

        Example:
            To just get a quicklook of the reflectivity to your screen try:

            >>> coral = Radar(start="2017040215",end="201704021530", device="CORAL")
            >>> coral.quickplot2D(value=coral.getReflectivity(),ylim=(100,2000))

        """
        import matplotlib.pyplot as plt

        _time = self.getTime()
        _range = self.getRange()

        fig, ax1 = plt.subplots(nrows=1, ncols=1, figsize=(9, 6))
        con = ax1.contourf(_time, _range, value.transpose(), cmap="jet")
        if ylim:
            ax1.set_ylim(ylim)
        ax1.grid()
        cl = plt.colorbar(con, ax=ax1)
        plt.show()

        if save_name:
            if not save_path:
                save_path = ""
            plt.savefig(save_path + save_name)

    def __getPostProcessingForVersion(self):
        """
        Function for reading the valid reflectivity values from the initiation file.

        Returns:
            List of valid reflectivity-postprocessing strings, for example:
            ["Zf","Ze","Zu"]
        """

        _vars = BCO.config[self._instrument]["VERSION_%i_REFLECTIVITY_VARIABLES"%self.data_version].split(",")
        return _vars


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


if __name__ == "main":
    pass
