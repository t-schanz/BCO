"""
This toolbox contains some functions which are being used by the MPPy package but might be usefull to the
enduser, as well.
"""

import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import datetime
import os
from ftplib import FTP
import BCO
from configparser import ConfigParser
import glob

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


def download_from_zmaw_ftp(device,start,end,output_folder):

    devs = ["CORAL","KATRIN","CEILOMETER","RADIATION","WEATHER","WINDLIDAR"]
    assert device in devs


    if not output_folder.lstrip()[-1] == "/":
        output_folder += "/"

    files = []

    _path_addition = BCO.config[device]["PATH_ADDITION"]
    _instrument = BCO.config[device]["INSTRUMENT"]

    for _date in daterange(start.date(), end.date()):
        if not _path_addition:
            _nameStr = getFileName(_instrument, _date,use_ftp=True).split("/")
        else:
            _nameStr = "/".join(getFileName(_instrument, _date,use_ftp=True).split("/"))

        files.append(_nameStr)

    # download the file:
    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)

    for file in files:
        file_to_retrieve = ftp.nlst(file)[0]
        try:
            __save_file = file_to_retrieve.split("/")[-1]
        except:
            __save_file = file_to_retrieve

        if not os.path.isfile(output_folder + __save_file): # check if the file is already there:
            print("Downloading %s"%__save_file)
            os.system("touch %s"%output_folder+__save_file)
            ftp.retrbinary('RETR ' + file_to_retrieve, open(output_folder + __save_file, 'wb').write)
        else:
            print("File already in provided output folder. No need to download it again.")
    ftp.close()


def getFileName(instrument, date, use_ftp=BCO.USE_FTP_ACCESS):

    # check if instrument is supported:
    instruments = ["CORAL", "KATRIN", "CEILOMETER", "RADIATION", "WEATHER", "WINDLIDAR"]
    assert instrument in instruments

    # check if date is in right format:
    assert type(date) in [dt, datetime.date]


    # get the right variable from settings.ini
    if not use_ftp:
        tmp_path = BCO.config[instrument]["PATH"]

    else:
        tmp_path = BCO.config[instrument]["FTP_PATH"]

    print(tmp_path)

    # handle paths including data versions:
    if BCO.config[instrument]["DATA_VERSION"] != "None":
        tmp_path += BCO.config[instrument]["DATA_VERSION"]

    # handle paths including dates:
    path_addition = ""
    if BCO.config[instrument]["PATH_ADDITION"] != "None":
        path_addition = BCO.config[instrument]["PATH_ADDITION"]
        tmp_path += date.strftime(path_addition)

    tmp_path += date.strftime(BCO.config[instrument]["NAME_SCHEME"])

    # get the resolved filename:
    if not use_ftp:
        name = glob.glob(tmp_path)

    else:
        ftp = FTP(BCO.FTP_SERVER)
        ftp.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)
        name = ftp.nlst(tmp_path)
        ftp.close()

    print(tmp_path)
    print(name)

    # make sure only one file with that name was found:
    assert len(name) == 1
    name = name[0]

    return name

def getFTPClient(user=None,passwd=None):

    if not user:
        user = BCO.FTP_USER
        passwd = BCO.FTP_PASSWD

    if not user:
        print("User and password need to be provided either via parameters to \n"
                "this function or by using the BCO.settings.path_to_ftp_file() function.")

    assert user
    assert passwd

    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=passwd, passwd=passwd)
    return ftp
