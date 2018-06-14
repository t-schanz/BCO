import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.dates as mdate
import collections
import time

class ClassTesting(object):

    def __init__(self,start=None,end=None,duration=None):

        if start == None:
            lower = dt(2016,1,1).timestamp()
            upper = dt(2018,6,14).timestamp()
            f = np.random.randint(lower,upper)
            self.start = dt.fromtimestamp(f)
            if duration == None:
                duration = np.random.randint(0,5)
            self.end = self.start + timedelta(days=duration)

        else:
            self.start = start
            self.end = end

    def testEverything(self):
        self.testRadar()
        self.testCeilometer()
        self.testWeather()
        self.testWindlidar()
        self.testRadiation()


    def testRadar(self,device="CORAL",version=2):
        print("==========================================")
        print("||>>>Testing %s          "%device)
        print("||>>>Timeframe from %s to %s"%(self.start.strftime("%x"),self.end.strftime("%x")))
        print("==========================================")

        from BCO.Instruments import Radar

        coral = Radar(start=self.start, end=self.end, device=device, version=version)

        ref = coral.getReflectivity(postprocessing="Zf")
        assert isinstance(ref,collections.Iterable)
        del ref



        ref = coral.getTime()
        info = ("\n========================================================\n"
                "Error occured while testing the >>>getTime()<<< method \n"
                "self.end.day=%i \n"
                "ref[-1].day =%i \n"
                "========================================================" % (self.end.day, ref[-1].day))
        assert (ref[-1]-timedelta(hours=1)).day == self.end.day , info
        del ref



        ref = coral.getLDR()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getVelocity()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getTime()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getMeltHeight()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getRadarConstant()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getNoisePower(channel="Co")
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getLDR()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getRMS()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getSNR()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getRange()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = coral.getTransmitPower()
        assert isinstance(ref,collections.Iterable)
        del ref

        print("===========================================")
        print("||>>> Radar test Finished succesfully <<<||")
        print("===========================================")


    def testWindlidar(self):
        from BCO.Instruments import Windlidar

        print("==========================================")
        print("||>>>Testing the Windlidar          ")
        print("||>>>Timeframe from %s to %s"%(self.start.strftime("%x"),self.end.strftime("%x")))
        print("==========================================")

        lidar = Windlidar(start=self.start,end=self.end)


        ref = lidar.getTime()
        info = ("\n========================================================\n"
                "Error occured while testing the >>>getTime()<<< method \n"
                "self.end.day=%i \n"
                "ref[-1].day =%i \n"
                "========================================================" % (self.end.day, ref[-1].day))
        assert (ref[-1] - timedelta(hours=1)).day == self.end.day, info
        del ref


        ref = lidar.getRange()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = lidar.getIntensity()
        assert isinstance(ref,collections.Iterable)
        del ref

        ref = lidar.getVelocity()
        assert isinstance(ref,collections.Iterable)
        del ref

        print("===============================================")
        print("||>>> Windlidar test Finished succesfully <<<||")
        print("===============================================")


    def testCeilometer(self):
        pass

    def testWeather(self):
        pass

    def testRadiation(self):
        pass


