import sys
from datetime import datetime as dt
import datetime
from MPPy.Devices.Device_module import Device
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
    Class for working with radar data from Barbados.
    Currently supported devices: -CORAL
    """
    def __init__(self, start, end, device="CORAL", version=2):
        self.__checkInput(device, version)
        self.start = self.getTime(start)
        self.end = self.getTime(end)
        self.device = device
        self.data_version = version
        self.path = self.__getPath()



    def __str__(self):
        returnStr = "%s Radar.\nUsed data version %i.\nLoad data from %s to %s." % \
                    (self.device, self.data_version, self.start, self.end)
        return returnStr



    def __checkInput(self, device, version):
        if device != "CORAL" and device != "KATRIN":
            print("The only devices allowed are CORAL and KATRIN.\n%s is not a valid device!" % device)
            sys.exit(1)

        _versions_avail = [1, 2, 3]
        if not version in _versions_avail:
            print(
                "The version of the Dataset needs to be between %i and %i" % (_versions_avail[0], _versions_avail[-1]))
            sys.exit(1)



    def reflectivity(self):
        dbz_list = []
        for _date in tools.daterange(self.start,self.end):
            _nameStr = "MMCR__MBR__Spectral_Moments*%s.nc"%tools.datestr(_date)
            _file = glob.glob(self.path + _nameStr)[0]

            nc = Dataset(_file,mode="r")
            dbzFromDate = nc.variables["Zf"][:].copy()
            dbz_list.append(dbzFromDate)
            nc.close()

        dbz = dbz_list[0]
        if len(dbz_list) > 1:
            for item in dbz_list:
                dbz = np.concatenate((dbz,item))

        return dbz



    def time(self):
        time_list = []
        for _date in tools.daterange(self.start,self.end):
            _nameStr = "MMCR__MBR__Spectral_Moments*%s.nc"%tools.datestr(_date)
            _file = glob.glob(self.path + _nameStr)[0]

            nc = Dataset(_file,mode="r")
            timeFromDate = nc.variables["time"][:].copy()
            time_list.append(timeFromDate)
            nc.close()

        time = time_list[0]
        if len(time_list) > 1:
            for item in time_list:
                time = np.concatenate((time,item))

        time = tools.num2time(time) # converting seconds since 1970 to datetime objects
        return time



    def range(self):
        for _date in tools.daterange(self.start,self.end):
            continue

        _nameStr = "MMCR__MBR__Spectral_Moments*%s.nc"%tools.datestr(_date)
        _file = glob.glob(self.path + _nameStr)[0]
        nc = Dataset(_file,mode="r")
        range = nc.variables["range"][:].copy()

        return range



    def __getPath(self):
        if self.device == "CORAL":
            __versionStr = "Version_%i" % self.data_version
            PATH = "/pool/OBS/BARBADOS_CLOUD_OBSERVATORY/Level_1/B_Reflectivity/%s/" % __versionStr

        return PATH




    def keys(self):
        __keys = ['reflectivity','time']
        return __keys



    def help(self):
        print("This class provides acces to the radar data from the Max-Planck-Institute owned radars on Barbados.\n" \
              ""
              )
