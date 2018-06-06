"""
This module contains functions to convert units.
"""
from datetime import datetime as dt
from datetime import timedelta


import numpy as np


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

    if type(num) == np.ndarray:
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

    if type(time) == np.ndarray:
        epo = lambda x: x.timestamp()

        date = np.asarray(list(map(epo, time)))
    else:
        date = time.timestamp()

    if utc:
        date = np.subtract(date,timedelta(hours=1).seconds)
    return date