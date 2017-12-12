from MPPy.Instruments import Radar
from MPPy.tools import tools
import numpy as np
from datetime import datetime as dt
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # coral  = Radar(start="20140813092350",end="20140913000050", device="KATRIN")
    coral = Radar(start="2017040215",end="201704021530", device="CORAL")
    # ref = coral.getReflectivity(postprocessing="Ze")
    vel = coral.getVelocity()
    # time = coral.getTime()
    # range = coral.getRange()
    coral.quickplot2D(vel,ylim=(100,2000))

