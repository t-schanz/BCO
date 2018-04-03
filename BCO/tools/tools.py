"""
This toolbox contains some functions which are being used by the MPPy package but might be usefull to the
enduser, as well.
"""

import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import os


__all__ = [
    'daterange',
    'num2time',
    'time2num',
    'datestr'
]

def daterange(start_date, end_date):
    """
    This function is for looping over datetime.datetime objects within a timeframe from start_date to end_date.
    It will only loop over days.

    Args:
        start_date: datetime.datetime object
        end_date: datetime.datetime object

    Yields:
        A datetime.datetime object starting from start_date and going to end_date

    Example:
        If you want to loop over the dates from the 1st January 2017 to the 3rd January 2017:

        >>> start = datetime.datetime(2017,1,1)
        >>> end = datetime.datetime(2017,1,3)
        >>> for x in daterange(start,end):
        >>>     print(str(x))
        2017-01-01 00:00:00
        2017-01-02 00:00:00
        2017-01-03 00:00:00
    """

    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)



def num2time(num):
    """
    Converts seconds since 1970 to datetime objects.
    If input is a numpy array, ouput will be a numpy array as well.

    Args:
        num: float/ndarray.  seconds since 1970

    Returns:
        datetime.datetime object
    """

    if type(num) == np.ndarray:
        f = np.vectorize(dt.fromtimestamp)
        date = f(num)
    else:
        date = dt.fromtimestamp(num)
    return date


def time2num(time):
    """
    Converts a datetime.datetime object to seconds since 1970 as float.
    If input is a numpy array, ouput will be a numpy array as well.

    Args:
        time: datetime.datetime object / ndarray of datetime.datetime objects.

    Returns:
        Float of seconds since 1970 / ndarray of floats.
    """

    if type(time) == np.ndarray:
        epo = lambda x: x.timestamp()

        date = np.asarray(list(map(epo, time)))
    else:
        date = time.timestamp()
    return date


def datestr(dt_obj):
    """
    Converts a datetime.datetime object to a string in the commonly used shape for this module.

    Args:
        dt_obj: datetime.datetime object.

    Returns:
        String of the format YYMMDD. Y=Year, M=Month, D=Day.
    """

    return dt_obj.strftime("%y%m%d")


def bz2Dataset(bz2file: str):
    """
    Generates a netCDF Dataset from a .nc.bz2 file. It therefore needs the "dummy_nc_file.nc".

    Args:
        bz2file: String: Path to the .nc.bz2 file.

    Returns:
        netCDF4.Dataset of the .nc.bz2 file.
    
    Example:
        To open a usual Dataset as known from the netCDF4 module use

        >>> nc = bz2Dataset("radar_testfile.nc.bz2")

        You then can work with this dataset the same as you would with a common netCDF4.Dataset:

        >>> reflectivity = nc.variables["zf"][:].copy()

    """
    from netCDF4 import Dataset
    import bz2

    package_directory = os.path.dirname(os.path.abspath(__file__))
    dummy_nc_file = package_directory + "/dummy_nc_file.nc"

    bz2Obj = bz2.BZ2File(bz2file)
    nc = Dataset(dummy_nc_file,memory=bz2Obj.read())
    return nc

