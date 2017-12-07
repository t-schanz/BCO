from MPPy.Devices.Radar import Radar
from MPPy.tools import tools
import numpy as np

if __name__ == "__main__":
    coral  = Radar(start="20140808",end="20140814", device="KATRIN")
    ref = coral.getReflectivity()
    time = coral.getTime()
    range = coral.getRange()

