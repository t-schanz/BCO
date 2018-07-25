"""
This toolbox contains some functions which are being used by the MPPy package but might be usefull to the
enduser, as well.

>>> import BCO.tools.tools

"""

import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import datetime
import os
from ftplib import FTP
import BCO
import glob


__all__ = [
    'daterange',
    'datestr',
    'bz2Dataset',
    'download_from_zmaw_ftp',
    'getFileName',
    'getFTPClient'

]

def daterange(start_date, end_date, step="day"):
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


    if step == "day":
        for n in range(int((end_date - start_date).days) + 1):
            yield start_date + timedelta(n)


    if step == "month":
        for y in range(int(end_date.year - start_date.year) + 1):

            _start = 1
            _end = 12

            if y + start_date.year == end_date.year:
                _end = end_date.month

            if y + start_date.year == start_date.year:
                _start = start_date.month

            for m in np.arange(_start,_end+1):
                _y = start_date.year + y
                # print(_start, _end,_y,m)
                yield dt(_y,m,1)


def datestr(dt_obj):
    """
    Converts a datetime.datetime object to a string in the commonly used shape for this module.

    Args:
        dt_obj: datetime.datetime object.

    Returns:
        String of the format YYMMDD. Y=Year, M=Month, D=Day.
    """

    return dt_obj.strftime("%y%m%d")


def bz2Dataset(bz2file):
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


    bz2Obj = bz2.BZ2File(bz2file)
    try:
        dummy_nc_file = package_directory + "/dummy_nc_file.nc"
        nc = Dataset(dummy_nc_file,memory=bz2Obj.read())
    except: # does not yet work:
        print("This function only works with netCDF-4 Datasets.")
        print("If the datamodel of your netcdf file is e.g 'classic' instead of" +
              " 'netCDF-4' it will break.")
        dummy_nc_file = package_directory + "/MRR__CIMH__LWC__60s_100m__20180520.nc"
        nc = Dataset(filename=dummy_nc_file,mode="r", memory=bz2Obj.read())
    return nc


def download_from_zmaw_ftp(device,start,end,output_folder="./",ftp_client=None):
    """
    This function can be used to download data from the bco ftp-server
    to store it on your local machine.

    Args:
        device: str: one of: "CORAL","KATRIN","CEILOMETER","RADIATION","WEATHER","WINDLIDAR".
        start: datetime.datetime object: start of the timeframe of which data will be downloaded.
        end:  datetime.datetime object: end of the timeframe of which data will be downloaded.
        output_folder: str: Where to store the downloaded data.

    Returns:

    """

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
    _close_ftp_client = False
    if ftp_client == None:
        ftp_client = FTP(BCO.FTP_SERVER)
        ftp_client.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)
        _close_ftp_client = True

    for file in files:
        file_to_retrieve = ftp_client.nlst(file)[0]
        try:
            __save_file = file_to_retrieve.split("/")[-1]
        except:
            __save_file = file_to_retrieve

        if not os.path.isfile(output_folder + __save_file): # check if the file is already there:
            print("Downloading %s"%__save_file)
            os.system("touch %s"%output_folder+__save_file)
            ftp_client.retrbinary('RETR ' + file_to_retrieve, open(output_folder + __save_file, 'wb').write)
        else:
            print("File already in provided output folder. No need to download it again.")

    if _close_ftp_client:
        ftp_client.close()


def getFileName(instrument, date, use_ftp, filelist=[], ftp_client=None):
    """
    This function can be used to get the full path and name of the file as on
    the server. The path will vary if you are switching between the ftp-server or
    beeing inside the mpi-network.

    Examples:
        If you for example want to now  the name of the file holding the reflectivities
        from the coral radar on the 23.01.2018 and you are using the ftp-server:

            >>> from BCO.tools.tools import getFileName
            >>> from datetime import datetime as dt
            >>> print(getFileName("CORAL",date=dt(2018,1,23),use_ftp=True))
            '/B_Reflectivity/Version_2/MMCR__MBR__Spectral_Moments__10s__155m-25km__180123.nc'

    Args:
        instrument: str: one of "CORAL", "KATRIN", "CEILOMETER", "RADIATION", "WEATHER", "WINDLIDAR"
        date: datetime.datetime object: Date from when you want the name. (Names usually include the date.)
        use_ftp: boolean: Whether to use the ftp-access or not.

    Returns:
        String containing full path and name of the file.
    """

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

    # print(tmp_path)

    # handle paths including data versions:
    if BCO.config[instrument]["DATA_VERSION"] != "None":
        tmp_path += BCO.config[instrument]["DATA_VERSION"]

    # handle paths including dates:
    path_addition = ""
    if BCO.config[instrument]["PATH_ADDITION"] != "None":
        path_addition = BCO.config[instrument]["PATH_ADDITION"]
        tmp_path += date.strftime(path_addition)

    tmp_name = date.strftime(BCO.config[instrument]["NAME_SCHEME"])
    tmp_path += tmp_name

    # get the resolved filename:
    if not use_ftp:
        name = glob.glob(tmp_path)

    else:
        if len(filelist) == 0:
            if ftp_client == None:
                ftp_client = FTP(BCO.FTP_SERVER)
                ftp_client.login(user=BCO.FTP_USER, passwd=BCO.FTP_PASSWD)
                name = ftp_client.nlst(tmp_path)
                ftp_client.close()

            else:
                name = ftp_client.nlst(tmp_path)

        else:
            for fl in filelist:
                _path = list(os.path.split(fl))
                _name = os.path.join(_path[0], tmp_name)
                name = glob.glob(_name)
                if len(name) != 0:
                    break

    # print(tmp_path)
    # print(name)

    # make sure only one file with that name was found:
    assert len(name) == 1
    name = name[0]

    return name

def getFTPClient(user=None,passwd=None):
    """
    This function can be used to get an open ftp-client to our ftp-server using
    the python library 'ftplib'.

    Examples:
        The client can be used to browse the ftp-server
        in a python command line interface:

        >>> from BCO.tools.tools import getFTPClient
        >>> ftp = getFTPClient(user="Heinz",passwd="secret")

        To then e.g. show the content of the diretory:

        >>> ftp.dir()

    Args:
        user: str: Username
        passwd: str: Password

    Returns:
        ftplib.FTP object.

    """

    if user == None:
        user = BCO.FTP_USER
        passwd = BCO.FTP_PASSWD

    if not user:
        print("User and password need to be provided either via parameters to \n"
                "this function or by using the BCO.settings.path_to_ftp_file() function.")

    assert user
    assert passwd

    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=user, passwd=passwd)
    return ftp
