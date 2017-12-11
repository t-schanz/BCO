from MPPy.Instruments import Radar
from MPPy.tools import tools
import numpy as np

if __name__ == "__main__":
    # coral  = Radar(start="20140813092350",end="20140913000050", device="KATRIN")
    coral = Radar(start="20170101",end="201701021530", device="CORAL")
    ref = coral.getReflectivity(postprocessing="Ze")
    vel = coral.getVelocity()
    time = coral.getTime()
    range = coral.getRange()

