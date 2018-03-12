"""
This Module contains the Ceilometer class. This class is for easy working with the cloud base height.
"""

import sys
import bz2
import glob
import numpy as np
from datetime import timedelta

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

        self._instrument = "CEILOMETER"
        self._name_str = "CEILO__*__#.nc"
        self._dateformat_str = "%Y%m"
        self._ftp_files = []

        self.path = self._getPath()
        print(self.path)

        # Attributes:
        self.title = None
        self.devices = None
        self.temporalResolution = None
        self.location = None

        self.lat = None
        self.lon = None

        # self.__getAttributes()

    def __getAttributes(self):
        """
        Function to load the static attributes from the netCDF file.
        """

        self.title = self._getAttrFromNC("title")
        self.devices = self._getAttrFromNC("devices")
        self.temporalResolution = self._getAttrFromNC("resolution")[0]
        self.location = self._getAttrFromNC("location")


        self.lat = self._getValueFromNc("lat")
        self.lon = self._getValueFromNc("lon")




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

        time = tools.num2time(time)  # converting seconds since 1970 to datetime objects
        time = self._local2UTC(time)


        return time

    def getRadiation(self,scope,scattering=None):
        """
        Returns the timeseries for the radiation for the specified scope and scattering type.

        Mind that when scope=="LW", then scattering does not need to be provided, because longwave radiation is always
        measured diffuse. If scattering is provided anyway it will fall back to "diffuse".


        Args:
            scope: One of: "LW","SW". (LW = long wave,, SW = short wave)
            scattering: One of: "direct","diffuse","global"

        Returns:
            1-D numpy array of the radiation.
        """

        scopes = ["LW","SW"]
        scatterings = ["direct","diffuse","global"]

        def keys():
            """
            Get the keys for the parameters
            Returns:
                Parameter Keys
            """
            return "scopes: %s \nscatterings: %s"%(" ".join([s for s in scopes])," ".join([s for s in scopes]))



        if not scope in scopes:
            print("Scope needs to be either 'SW' (shortwave) or 'LW' (longwave)")
            return None

        if not scattering in scatterings:
            print("Scattering needs to be one of: %s"%" ,".join([s for s in scatterings]))


        if scope == "LW":
            if not scattering == "diffuse":
                print("Longwaveradiation at the surface is only measured as diffuse radiation. Setting scattering to diffuse!")

            _rad = self._getArrayFromNc("LWdown_diffuse")

        elif scope == "SW":

            _rad = self._getArrayFromNc("SWdown_%s"%scattering)

        return _rad


    def getVoltage(self,scope,scattering=None):
        """
        Returns the sensitivity timeseries for the specified scopte and scattering type.

        Mind that when scope=="LW", then scattering does not need to be provided, because longwave radiation is always
        measured diffuse. If scattering is provided anyway it will fall back to "diffuse".


        Args:
            scope: One of: "LW","SW". (LW = long wave,, SW = short wave)
            scattering: One of: "direct","diffuse","global"

        Returns:
            1-D numpy array of the voltage.
        """
        scopes = ["LW","SW"]
        scatterings = ["direct","diffuse","global"]

        def keys():
            """
            Get the keys for the parameters
            Returns:
                Parameter Keys
            """
            return "scopes: %s \nscatterings: %s"%(", ".join([s for s in scopes]),", ".join([s for s in scatterings]))

        if not scope:
            print("Following parameter configurations are allowed:")
            print(keys())
            return None

        if not scope in scopes:
            print("Scope needs to be either 'SW' (shortwave) or 'LW' (longwave)")
            return None

        if not scattering in scatterings:
            print("Scattering needs to be one of: %s"%" ,".join([s for s in scatterings]))


        if scope == "LW":
            if not scattering == "diffuse":
                print("Longwaveradiation at the surface is only measured as diffuse radiation. Setting scattering to diffuse!")

            _volt = self._getArrayFromNc("LWdown_diffuse_voltage")

        elif scope == "SW":

            _volt = self._getArrayFromNc("SWdown_%s_voltage"%scattering)

        return _volt

    def getSensitivity(self,instrument):
        """
        Returns the sensitivity timeseries for the specified instrument.

        Args:
            instrument: One of: "GeoSh", "AnoSh", "AnoGlob", "Hel"

        Returns:
            1-D numpy array of the sensitivity.

        """

        instruments = ["GeoSh", "AnoSh", "AnoGlob","Hel"]

        if instrument in instruments:
            _sens = self._getArrayFromNc("%s_Sensitivity"%instrument)

            return _sens

        else:
            print("Instruments must be one of: %s"%", ".join(instruments))
            return None

    def getTemperature(self, instrument):
        """
        Returns the temperature timeseries for the specified instrument.

        Args:
            instrument: One of: "GeoSh", "AnoSh", "AnoGlob", "Hel"

        Returns:
            1-D numpy array of the temperature.

        """

        instruments = ["GeoSh", "AnoSh", "AnoGlob", "Hel"]

        if instrument in instruments:
            _temp = self._getArrayFromNc("%s_temp" % instrument)

            return _temp

        else:
            print("Instruments must be one of: %s" % ", ".join(instruments))
            return None





