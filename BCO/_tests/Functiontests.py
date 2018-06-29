from datetime import datetime as dt

class ConverterTesting(object):
    def __init__(self):
        print("==========================================")
        print("||>>>Testing the converter functions      ")
        print("==========================================")


        from BCO.tools import convert

        val= convert.Celsius2Kelvin(0)
        assert val == 273.15
        del val

        val = convert.Kelvin2Celsius(273.15)
        assert val == 0
        del val

        val_in = dt(2018,1,1)
        val1 = convert.time2num(val_in)
        val2 = convert.num2time(val1)
        assert val2 == val_in
        del val_in,val1,val2

        print("=====================================")
        print("||>>> test finished succesfully <<<||")
        print("=====================================")

