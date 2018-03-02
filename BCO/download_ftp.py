from ftplib import FTP
import BCO
import tempfile

if __name__ == "__main__":
    ftp_path = '/WindLidar/'
    file = '"WindLidar__Deebles_Point*__180101.nc*"'

    BCO.settings.path_to_ftp_file("ftp_access.txt")

    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=BCO.FTP_USER,passwd=BCO.FTP_PASSWD)

    ftp_dir = []
    file_to_retrieve = ftp.nlst(ftp_path + file)[0]
    # ftp.dir(ftp_dir.append())

    tmp_dir = tempfile.gettempdir()
    ftp.nlst()
    # ftp.retrbinary('RETR ' +file_to_retrieve, open(tmp_dir+file_to_retrieve.split("/")[-1],"wb").write)

