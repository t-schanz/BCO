from MPPy.Devices.Radar import Radar
from MPPy.tools import tools
import numpy as np

if __name__ == "__main__":
    coral  = Radar(start="20140813092350",end="20140913000050", device="KATRIN")
    # coral = Radar(start="20160813",end="2016081312", device="CORAL")
    ref = coral.getReflectivity()
    time = coral.getTime()
    range = coral.getRange()

