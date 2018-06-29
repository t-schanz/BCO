# coding=utf-8

"""
This module contains functions to convert units.

>>> import BCO.tools.convert
"""
from datetime import datetime as dt
from datetime import timedelta
import collections
import numpy as np
import time as time_module
import sys


def Celsius2Kelvin(value):
    """
    Converts a Temperature from °C to K.

    Args:
        value: Value, list or array containing temperatures in °C.

    Returns:
        Same as input format, containing values in K.
    """
    return np.add(value,273.15)


def Kelvin2Celsius(value):
    """
    Converts a Temperature from K to °C.

    Args:
        value: Value, list or array containing temperatures in K.

    Returns:
        Same as input format, containing values in °C.
    """
    return np.subtract(value,273.15)


def num2time(num,utc=False):
    """
    Converts seconds since 1970 to datetime objects.
    If input is a numpy array, ouput will be a numpy array as well.

    Args:
        num: float/ndarray.  seconds since 1970

    Returns:
        datetime.datetime object
    """

    if isinstance(num,collections.Iterable):
        f = np.vectorize(dt.fromtimestamp)
        date = f(num)
    else:
        date = dt.fromtimestamp(num)

    if utc:
        f = np.vectorize(lambda x,y: x-y)
        date = f(date,timedelta(hours=1))

    return date


def time2num(time,utc=False):
    """
    Converts a datetime.datetime object to seconds since 1970 as float.
    If input is a numpy array, ouput will be a numpy array as well.

    Args:
        time: datetime.datetime object / ndarray of datetime.datetime objects.

    Returns:
        Float of seconds since 1970 / ndarray of floats.
    """
    if sys.version_info >= (3,0):
        if isinstance(time,collections.Iterable):
            epo = lambda x: x.timestamp()

            date = np.asarray(list(map(epo, time)))
        else:
            date = time.timestamp()

    else:

        if isinstance(time, collections.Iterable):
            epo = lambda x: dt.fromtimestamp(x)
            date = np.asarray(list(map(epo, time)))
            date = time_module.mktime(date.timetuple())
        else:

            date = time_module.mktime(time.timetuple())

    if utc:
        date = np.subtract(date,timedelta(hours=1).seconds)
    return date