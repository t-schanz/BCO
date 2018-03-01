from ftplib import FTP
import BCO

if __name__ == "__main__":
    ftp_path = '/B_Reflectivity/Version_2/'
    file = 'MMCR__MBR__Spectral_Moments__10s__155m-25km__180226.nc'

    BCO.settings.path_to_ftp_file("ftp_access.txt")

    ftp = FTP(BCO.FTP_SERVER)
    ftp.login(user=BCO.FTP_USER,passwd=BCO.FTP_PASSWD)
    ftp.dir()
    ftp.retrbinary('RETR '+ftp_path+file, open(file, 'wb').write)

