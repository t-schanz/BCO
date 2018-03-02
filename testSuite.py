from BCO.Instruments import Radar
from BCO.Instruments import Windlidar
from BCO.Instruments import Radiation
import BCO

from BCO.tools import tools
# from BCO.Quicklooks import plot_RadarLidarVelcities

import numpy as np
from datetime import datetime as dt
# import matplotlib.pyplot as plt
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
    print(BCO.USE_FTP_ACCESS)
    BCO.settings.set_ftp(True)
    BCO.settings.path_to_ftp_file("BCO/ftp_access.txt")
    print(BCO.USE_FTP_ACCESS)

    lidar = Windlidar("20180101","20180101")


