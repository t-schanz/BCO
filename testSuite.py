from BCO.Instruments import Radar
from BCO.Instruments import Windlidar
from BCO.Instruments import Radiation
from BCO.Instruments import SfcWeather
from BCO.Instruments import Ceilometer
import BCO

from BCO.tools import tools
# from BCO.Quicklooks import plot_RadarLidarVelcities

import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt
from netCDF4 import Dataset


def testRadar():
    # coral  = Radar(start="20140813092350",end="20140913000050", device="KATRIN")
    coral = Radar(start="20180212",end="20180212", device="CORAL")
    ref = coral.getReflectivity(postprocessing="Ze")
    vel = coral.getVelocity()
    time = coral.getTime()
    range = coral.getRange()
    coral.quickplot2D(ref,ylim=(100,2000))


if __name__ == "__main__":
    # FTP-settings:

    BCO.settings.set_ftp(True)
    # BCO.settings.path_to_ftp_file("/home/tobias/Documents/ftp_access.txt")
    BCO.settings.path_to_ftp_file("/home/mpim/m300517/ftp_access.txt",verbose=True)
    # BCO.settings.path_to_ftp_file("C:/Users/darkl/Documents/ftp_access.txt")


    # working devices:
    #
    Rad = Radiation("20180103","20180104")
    rad_time = Rad.getTime()
    Wx = SfcWeather("20180101","20180101")
    wx_time = Wx.getTime()
    coral = Radar("20180129","20180130",device="CORAL")
    coral_time = coral.getTime()
    coral_pow = coral.getTransmitPower()
    # testRadar()
    # plt.plot(coral_time,coral_pow)
    # plt.show()
    lidar = Windlidar("20180401","20180410") #seems to work with data version 1.01!
    lidar_time = lidar.getTime()
    ceilo = Ceilometer("20170601","20170620") # can not work yet as the data is not there.
    ceilo_time = ceilo.getTime()

    # nc = tools.bz2Dataset(
    #     "/pool/OBS/BARBADOS_CLOUD_OBSERVATORY/Level_1/H_Liquid_water_content/201805/MRR__CIMH__LWC__60s_100m__20180523.nc.bz2")


