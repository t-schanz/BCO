# coding=utf-8

"""
This Module contains the SfcWeather class. This class is for easy working with data collected from the surface weather
station (height ~ 20m) at the BCO site.
"""

import sys
import bz2
import glob
import numpy as np
from datetime import timedelta

import BCO.tools.convert
from BCO.tools import tools
from BCO.tools import convert
from BCO.Instruments.Device_module import __Device
import BCO

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the BCO-package to work.")
    sys.exit(1)


class SfcWeather(__Device):
    """
    Class for working with the data collected by the ground weather station.


    Args:
            start: Either String or datetime.datetime-object indicating the start of the timewindow.
            end: Either String or datetime.datetime-object indicating the end of the timewindow.


    Attributes:
            start: datetime.datetime object indicating the beginning of the chosen timewindow.
            end: datetime.datetime object indicating the end of the chosen timewindow.
            title: Name of the device as in the netCDF file.
            device: Name of the device as in the Settings.ini.
            temporalResolution:
            location: Name of the location.
            position: Position of the instrument.
            height: height above surface.
            lat: Latitude of the instruments location.
            lon: Longitude of the instruments location.
    """

    def __init__(self, start, end):
        """
        Args:
            start: start of the timeframe.
            end: end of the timeframe.


        """

        self.start = self._checkInputTime(start) + timedelta(hours=0)
        self.end = self._checkInputTime(end) + timedelta(hours=0)

        self._instrument = "WEATHER"
        self._name_str = BCO.config[self._instrument]["NAME_SCHEME"]
        self._path_addition = BCO.config[self._instrument]["PATH_ADDITION"]
        self._ftp_files = []

        self.path = self._getPath()


        # Attributes:
        self.title = None
        self.device = None
        self.temporalResolution = None
        self.location = None
        self.position = None
        self.height = None


        self.lat = None
        self.lon = None

        self.__getAttributes()

    def __getAttributes(self):
        """
        Function to load the static attributes from the netCDF file.
        """

        self.title = self._getAttrFromNC("title")
        self.device = self._getAttrFromNC("devices")
        self.temporalResolution = self._getAttrFromNC("resolution")
        self.location = self._getAttrFromNC("location")
        self.position = self._getAttrFromNC("position")
        self.height = self._getAttrFromNC("height")


        self.lat = self._getValueFromNc("lat")
        self.lon = self._getValueFromNc("lon")




    def getTime(self):
        """
        Loads the time steps over the desired timeframe from all netCDF-files and returns them as one array.

        Returns:
            A numpy array containing datetime.datetime objects

        Example:
            Getting the time-stamps:

            >>> from BCO.Instruments import SfcWeather
            >>> met = SfcWeather("20180101","20180101")
            >>> met.getTime()
            array([datetime.datetime(2018, 1, 1, 0, 0, tzinfo=<UTC>),
                   datetime.datetime(2018, 1, 1, 0, 0, 10, tzinfo=<UTC>),
                   datetime.datetime(2018, 1, 1, 0, 0, 20, tzinfo=<UTC>), ...,
                   datetime.datetime(2018, 1, 1, 23, 59, 30, tzinfo=<UTC>),
                   datetime.datetime(2018, 1, 1, 23, 59, 40, tzinfo=<UTC>),
                   datetime.datetime(2018, 1, 1, 23, 59, 50, tzinfo=<UTC>)], dtype=object)


        """

        time = self._getArrayFromNc('time')

        time = BCO.tools.convert.num2time(time)  # converting seconds since 1970 to datetime objects
        time = self._local2UTC(time)

        return time

    def getDataQuality(self):
        """
        Get the data quality in percent.

        Returns:
            1D numpy array with the data quality in percent.
        """

        sdq = self._getArrayFromNc("SDQ")
        return sdq

    def getWindDirection(self):
        """
        Get the surface wind direction in deg.

        Returns:
            1D numpy array with wind direction in deg.
        """
        dir = self._getArrayFromNc("DIR")
        return dir

    def getWindSpeed(self,accumulation="mean"):
        """
        Get the windspeed in m/s.
        Since the data is only available at a specific temporal resolution (usually 10s) it needs to be
        accumulated in some way. By providing a "accumulation" parameter you can decide if you want the minimum,
        the mean or the maximum of this 10s accumulation.

        Args:
            accumulation: str: One of "mean", "min", "max". Default is mean.

        Returns:
            1D numpy array containing the windspeed in m/s.

        Example
        To get the 10s maximum values:

            >>> from BCO.Instruments import SfcWeather
            >>> met = SfcWeather("20180101","20180101")
            >>> max_velocity = met.getWindSpeed("max")


        """

        values = ["min","mean","max"]
        nc_vars = ["MNV","VEL","MXV"]

        nc_dict = dict(zip(values,nc_vars))

        __vel = self._getArrayFromNc(nc_dict[accumulation])
        return __vel

    def getTemperature(self,unit="K"):
        """
        Get the air temperature.

        Args:
            unit: return temperature in kelvin "K" or Celsius "C"

        Returns:
            1D numpy array containing the temperature in specified unit.

        """

        __t = self._getArrayFromNc("T")

        if unit == "C":
            return __t
        elif unit == "K":
            return convert.Celsius2Kelvin(__t)
        else:
            print("Not a valid temperature unit: %s.\n Use 'K' or 'C'."%unit)
            return None

    def getHumidity(self):
        """
        Get the relative humidity in percent.

        Returns:
            1D numpy array of the relative humidity in percent.
        """

        __RH = self._getArrayFromNc("RH")
        return __RH

    def getPressure(self):
        """
        Get preesure in hPa

        Returns:
            1D numpy array of the pressure in hPa.
        """
        __p = self._getArrayFromNc("P")
        return __p

    def getPrecipitation(self,value="RI"):
        """
        Get one of the following Rain properties:
            -   R: Amount of Rain in mm.
            -   RDS: Duration of rain in seconds.
            -   RDH: Duration of rain in hours.
            -   RI: Mean rain intensity in mm/h [Default].
            -   MXRI: Max rain intensity in mm/h.
            -   RP: Summit of rain intenstity in mm/h.

            -   H: Strikes of hail in cm⁻².
            -   HDS: Duration of hail in seconds.
            -   HDH: Durtaion of hail in hours.
            -   HI: Mean hail intensity in cm⁻².
            -   MXHI: Max hail intensity in cm⁻².
            -   HP: Summit of hail intensity in cm⁻².



        Args:
            value: str: one of "R","RDS","RDH","RI","MXRI","RP","H","HDS","HDH","HI","MXHI","HP"

        Returns:
            1D numpy array of the specified value.
        """

        values = ["R","RDS","RDH","RI","MXRI","RP","H","HDS","HDH","HI","MXHI","HP"]
        if not value in values:
            print("value needs to be one of %s" % ",".join(values))
            return None

        __var = self._getArrayFromNc(value)
        return __var

    def getTechnicalValues(self,value=None):
        """

            -   TI: Internal temperature in °C.
            -   TH: Heater temperature in °C.
            -   VH: Electric power at the heater in V.
            -   VS: Supply voltage in V.
            -   VR: Reference voltage in V.

        Args:
            value: str: one of "TI", "TH", "VH", "VS", "VR"

        Returns:
            1D numpy array of the specified value.
        """

        values = ["TI", "TH", "VH", "VS", "VR"]

        if not value:
            print("value needs to be one of: %s"%",".join(values))

        __var = self._getArrayFromNc(value)
        return __var







