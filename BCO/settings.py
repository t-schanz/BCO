"""
Module for setting global attributes.
"""


import BCO

def set_ftp(ftp,user=None,passwd=None):
    """
    Function to set-up ftp-access.

    User and Password can be set via this function or via providing a file
    containing those. For more information pls have a look at the documentation
    on how to set up this package for ftp-access.

    Args:
        ftp: Boolean. If true the package will use ftp connection for data access.
        user: Username for the ftp-server.
        passwd: Password for the ftp-server.
    Example:

        >>> from BCO import settings
        >>> settings.set_ftp(True)

        Now the package would try to retrieve all data using the ftp-server,
        but you need to provide your username and password via the
        path_to_ftp_file function. If you want to submit your username and
        password with plain text in the code (not recommended):

        >>> settings.set_ftp(True, user="Heinz", passwd="secret")

    """

    BCO.USE_FTP_ACCESS = ftp

    if (user and passwd):
        BCO.FTP_USER = user
        BCO.FTP_PASSWD = passwd


def path_to_ftp_file(file_path,verbose=True):
    """
    Sets the path to the file with the username and password in it.
    Please do not have this file in the same directory as you other python files and
    make sure it is not under version control. The file should contain just two lines:

    ExampleFile:
        user=test_user
        passwd=my_passwd

    Args:
        file_path: string: Path to the file with username and password.

    Example:
        >>> from BCO import settings
        >>> settings.path_to_ftp_file("/home/wherever/myinfos.txt")
        >>> settings.set_ftp(True)

    Now the package will use the given username and password to access the ftp server to retrieve the data.
    """
    with open(file_path,"r") as f:
        lines = f.readlines()

    for line in lines:
        if "user" in line.lower():
            BCO.FTP_USER = line.split("=")[1].rstrip()

        if "passw" in line.lower():
            BCO.FTP_PASSWD = line.split("=")[1].rstrip()

    if verbose:
        print("Successfully loaded username and password")

def setConfig(device,parameter,new_parameter_value):

    BCO.config[device][parameter] = new_parameter_value