import numpy as np
from datetime import datetime as dt
from datetime import timedelta


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def num2time(num):
    if type(num) == np.ndarray:
        f = np.vectorize(dt.fromtimestamp)
        date = f(num)
    else:
        date = dt.fromtimestamp(num)
    return date

def datestr(dt_obj):
    return dt_obj.strftime("%y%m%d")