from MPPy.Instruments import Radar
from MPPy.Instruments import Windlidar
from MPPy.tools import tools

import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt
from netCDF4 import Dataset


def testRadar():
    coral  = Radar(start="20140813092350",end="20140913000050", device="KATRIN")
    coral = Radar(start="2017040215",end="201704021530", device="CORAL")
    ref = coral.getReflectivity(postprocessing="Ze")
    vel = coral.getVelocity()
    time = coral.getTime()
    range = coral.getRange()
    coral.quickplot2D(vel,ylim=(100,2000))

if __name__ == "__main__":
    lidar = Windlidar(start="20180101",end="20180101")



