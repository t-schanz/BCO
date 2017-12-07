import numpy as np
from datetime import datetime as dt
from datetime import timedelta


def daterange(start_date, end_date):
    """

    :param start_date: datetime.datetim object
    :param end_date: datetime.datetime object
    :return:
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def num2time(num):
    """
    Converts seconds since 1970 to datetime objects.
    If input is a numpy array, ouput will be a numpy array as well.

    :param num: float/ndarray.  seconds since 1970
    :return: datetime.datetime object
    """

    if type(num) == np.ndarray:
        f = np.vectorize(dt.fromtimestamp)
        date = f(num)
    else:
        date = dt.fromtimestamp(num)
    return date


def datestr(dt_obj):
    """
    Converts a datetime.datetime object to a string in the commonly used shape for this module.

    :param dt_obj: datetime.datetime object
    :return: string of the format YYMMDD. Y:Year, M:Month, D:Day
    """
    return dt_obj.strftime("%y%m%d")
