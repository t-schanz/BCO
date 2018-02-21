from BCO.Instruments import Radar
from BCO.Instruments import Windlidar
from BCO.tools import tools
from BCO.Quicklooks import plot_RadarLidarVelcities

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
    # testRadar()
    # coral = Radar(start="20180212", end="201802122359", device="CORAL")
    # lidar = Windlidar(start="20180101",end="20180101")

    coral = Radar("20180101","2018010315")
    coral_time = coral.getTime()
    coral_range = coral.getRange()
    coral_ref = coral.getReflectivity(postprocessing="Zu")

    # fig = plt.figure()
    # plt.contourf(coral_time,coral_range, coral_ref.transpose())
    # plt.savefig("coral_tutorial1.png")

    # coral.quickplot2D(coral.getReflectivity(),save_name="coral_tutorial2.png")

    # plot_RadarLidarVelcities("20170723")