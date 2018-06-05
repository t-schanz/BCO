"""
Blueprint for creating new Instrument modules.

"""


import BCO
from BCO import tools
from BCO.Instruments.Device_module import __Device

class Instrument(__Device):
    def __init__(self, start, end, device="CORAL", version=2):

        self.start = self._checkInputTime(start)
        self.end = self._checkInputTime(end)

        self.skipped = None # needed to store skipped dates.

        self._instrument = "NAME_OF_INSTRUMENT_IN_INI"  # String used for retrieving the filepath from settings.ini
        self._name_str = "GENERAL_NAME_%s_STRUCTURE.nc" % ( "#")  # general name-structure of file.
                                                                            # "#" indicates where date will be replaced
        self._dateformat_str = "%y%m%d" # the datetime format this instrument uses
        self._ftp_files = []

        if BCO.USE_FTP_ACCESS:
            for _date in tools.daterange(self.start.date(), self.end.date()):
                _datestr = _date.strftime(self._dateformat_str)
                _nameStr = self._name_str.replace("#", _datestr)
                print(_nameStr)
                self.path = self._downloadFromFTP(ftp_path=getValueFromSettings("RADAR_PATH"), file=_nameStr)

        else:
            self.path = self.__getPath()




    def __str__(self):
        returnStr = "%s Radar.\nUsed data version %i.\nLoad data from %s to %s." % \
                    (self.device, self.data_version, self.start, self.end)
        return returnStr

