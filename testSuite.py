from BCO.Instruments import Radar
from BCO.Instruments import Windlidar
from BCO.Instruments import Radiation
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
    BCO.settings.set_ftp(True)
    BCO.settings.path_to_ftp_file("/home/tobias/Documents/ftp_access.txt")



    # lidar = Windlidar("20180101","20180101")
    Rad = Radiation("20180101","20180101")
    Rad.getTime()
    # coral = Radar("20180101","20180101")
    # met = BCO.Instruments.SfcWeather("20180101","20180103")
    # plt.plot(Rad.getTime())
    # plt.show()



