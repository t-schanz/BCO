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
        from BCO.Instruments import Ceilometer

        print("==========================================")
        print("||>>>Testing the Ceilometer          ")
        print("||>>>Timeframe from %s to %s"%(self.start.strftime("%x"),self.end.strftime("%x")))
        print("==========================================")

        dev = Ceilometer(start=self.start,end=self.end)


        ref = dev.getTime()
        info = ("\n========================================================\n"
                "Error occured while testing the >>>getTime()<<< method \n"
                "self.end.day=%i \n"
                "ref[-1].day =%i \n"
                "========================================================" % (self.end.day, ref[-1].day))
        assert (ref[-1] - timedelta(hours=1)).day == self.end.day, info
        del ref

        ref = dev.getCBH()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getInstrumentStatusFlag()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getJenoptikOutputFlag()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getMRRStatusFlag()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getRainFlag()
        assert isinstance(ref, collections.Iterable)
        del ref


        print("===========================================")
        print("||>>> Ceilometer test Finished succesfully <<<||")
        print("===========================================")


    def testWeather(self):
        from BCO.Instruments import SfcWeather

        print("==========================================")
        print("||>>>Testing the SfcWeather          ")
        print("||>>>Timeframe from %s to %s" % (self.start.strftime("%x"), self.end.strftime("%x")))
        print("==========================================")

        dev = SfcWeather(start=self.start, end=self.end)

        ref = dev.getTime()
        info = ("\n========================================================\n"
                "Error occured while testing the >>>getTime()<<< method \n"
                "self.end.day=%i \n"
                "ref[-1].day =%i \n"
                "========================================================" % (self.end.day, ref[-1].day))
        assert (ref[-1] - timedelta(hours=1)).day == self.end.day, info
        del ref

        ref = dev.getPrecipitation()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getWindDirection()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getDataQuality()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getHumidity()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getPressure()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getTechnicalValues(value="TI")
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getTemperature()
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getWindSpeed()
        assert isinstance(ref, collections.Iterable)
        del ref


        print("===========================================")
        print("||>>> Weather test Finished succesfully <<<||")
        print("===========================================")


    def testRadiation(self):
        from BCO.Instruments import Radiation

        print("==========================================")
        print("||>>>Testing the Radiation          ")
        print("||>>>Timeframe from %s to %s" % (self.start.strftime("%x"), self.end.strftime("%x")))
        print("==========================================")

        dev = Radiation(start=self.start, end=self.end)

        ref = dev.getTime()
        info = ("\n========================================================\n"
                "Error occured while testing the >>>getTime()<<< method \n"
                "self.end.day=%i \n"
                "ref[-1].day =%i \n"
                "========================================================" % (self.end.day, ref[-1].day))
        assert (ref[-1] - timedelta(hours=1)).day == self.end.day, info
        del ref

        ref = dev.getRadiation(scope="LW")
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getSensitivity(instrument="GeoSh")
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getTemperature("GeoSh")
        assert isinstance(ref, collections.Iterable)
        del ref

        ref = dev.getVoltage("LW")
        assert isinstance(ref, collections.Iterable)
        del ref


        print("===============================================")
        print("||>>> Radiation test Finished succesfully <<<||")
        print("===============================================")