import sys
from datetime import datetime as dt
import datetime
from MPPy.Devices.Device_module import Device

try:
    from netCDF4 import Dataset
except:
    print("The module netCDF4 needs to be installed for the MPPy-package to work.")
    sys.exit(1)


class Radar(Device):
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
        nc = Dataset()

    def __getPath(self):
        if self.device == "CORAL":
            __versionStr = "Version_%i" % self.data_version
            PATH = "/pool/OBS/BARBADOS_CLOUD_OBSERVATORY/Level_1/B_Reflectivity/%s/" % __versionStr

    def keys(self):
        __keys = ['reflectivity', ]
        return __keys

    def help(self):
        print("This class provides acces to the radar data from the Max-Planck-Institute owned radars on Barbados.\n" \
              ""
              )
