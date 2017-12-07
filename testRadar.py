from MPPy.Devices.Radar import Radar
import numpy as np

if __name__ == "__main__":
    coral  = Radar(start="20170108",end="2017011")
    ref = coral.reflectivity()
    time = coral.time()
    range = coral.range()