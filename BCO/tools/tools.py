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

    def getfilenames(dev):
        namestrings = []
        for _date in daterange(dev.start.date(), dev.end.date()):
            _datestr = _date.strftime(dev._dateformat_str)
            tmp_nameStr = dev._name_str.replace("#", _datestr)
            namestrings.append(tmp_nameStr)

        return namestrings


    if not output_folder.lstrip()[-1] == "/":
        output_folder += "/"


    # get the path on the ftp-server:
    package_directory = os.path.dirname(os.path.abspath(__file__))
    ini_file = package_directory + "/../ftp_settings.ini"
    __counter = 0
    with open(ini_file, "r") as f:
        while __counter < 1e5:
            try:
                line = f.readline().rstrip()
                if device.upper() + "_PATH:" in line:
                    ftp_path =  line.split(":")[1]
                __counter += 1
            except:
                break

    # get the file_name:
    if device == "CORAL":
        dev = BCO.Instruments.Radar(start,end,device)
    if device == "KATRIN":
        dev = BCO.Instruments.Radar(start,end,device)
    if device == "CEILOMETER":
        dev = BCO.Instruments.Ceilometer(start,end)
    if device == "RADIATION":
        dev = BCO.Instruments.Radiation(start,end)
    if device == "WEATHER":
        dev = BCO.Instruments.SfcWeather(start,end)
    if device == "WINDLIDAR":
        dev = BCO.Instruments.Windlidar(start,end)

    assert dev

    files = getfilenames(dev)



    # download the file:
    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)

    for file in files:
        file_to_retrieve = ftp.nlst(ftp_path + file)[0]
        try:
            __save_file = file_to_retrieve.split("/")[-1]
        except:
            __save_file = file_to_retrieve

        if not os.path.isfile(output_folder + __save_file): # check if the file is already there:
            print("Downloading %s"%__save_file)
            ftp.retrbinary('RETR ' + file_to_retrieve, open(output_folder + __save_file, 'wb').write)
        else:
            print("File already in provided output folder. No need to download it again.")


def getFileName(instrument, date, use_ftp=BCO.USE_FTP_ACCESS):

    # check if instrument is supported:
    instruments = ["CORAL", "KATRIN", "CEILOMETER", "RADIATION", "WEATHER", "WINDLIDAR"]
    assert instrument in instruments

    # check if date is in right format:
    assert type(date) in [dt, datetime.date]

    # special treatment for Radars:
    if instrument in ["CORAL","KATRIN","KIT"]:
        device = instrument
        instrument = "RADAR"
        if device == "CORAL":
            device = "MBR"

    # get the right variable from settings.ini
    if not use_ftp:
        tmp_path = BCO.config[instrument]["PATH"]

    else:
        tmp_path = BCO.config[instrument]["FTP_PATH"]

    # handle paths including dates:
    path_addition = ""
    if BCO.config[instrument]["PATH_ADDITION"] != "None":
        path_addition = BCO.config[instrument]["PATH_ADDITION"]
        tmp_path += date.strftime(path_addition)



    # Again extra treatment for Radar:
    if instrument == "RADAR":
        tmp_path += date.strftime(BCO.config[instrument]["NAME_SCHEME"].replace("%s",device))
    else:
        tmp_path += date.strftime(BCO.config[instrument]["NAME_SCHEME"])

    # get the resolved filename:
    if not use_ftp:
        name = glob.glob(tmp_path)

    else:
        ftp = FTP(BCO.FTP_SERVER)
        ftp.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)
        name = ftp.nlst(tmp_path)
        ftp.close()


    # make sure only one file with that name was found:
    assert len(name) == 1
    name = name[0]

    return name


