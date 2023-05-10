import tarfile
from pathlib import Path
import os
import io
import util

class DoesNotExist(Exception):
    pass
class NotSosReport(Exception):
    pass
class CannotRead(Exception):
    pass
class FileNotFoundInReport(Exception):
    pass

class SosReport:
    """
    A class symbolizing a sosreport
    a sosreport can be a folder or a compressed archive
    normal workflows include:
        checking that the sosreport is valid by checking for a "version.txt" file
        and extracting files from the sosreport
    """

    def __init__(self, report):
        self._report = Path(report)
        #self._is_archive = False

        if not ( self._report.exists() ):
            raise DoesNotExist(f"Could not find sosreport: {self._report}")
        
        if not (self._is_sosreport(self._report)):
            _r = self._report
            raise NotSosReport(
                f"Sos report should be a tar.xz archive or a directory; instead: {_r}"
                )
        
    def _is_sosreport(self, report):
        _report = Path(report)
        if _report.is_file():
            return self._is_archive_sosreport(report)
        else:
            return self._is_dir_sosreport(report)

    def _is_dir_sosreport(self, report):
        _report = Path(report)

        if not os.access(_report, os.R_OK):
            raise CannotRead(f"Cannot read report: {_report}")

        if not (_report.exists() and _report.is_dir()):
            return False
        
        _version = _report / "version.txt"

        if not (_version.exists()):
            return False
        
        if "sosreport" not in _version.read_text():
            return False
        
        return True

    def _is_archive_sosreport(self, report):
        _report = Path(report)

        if not os.access(_report, os.R_OK):
            raise CannotRead(f"Cannot read report: {_report}")

        if not (_report.exists() and _report.is_file()):
            return False
        
        if not tarfile.is_tarfile(_report):
            return False
        
        """
        Check for 'version.txt' in the archive

        a standard pattern for sos report archives seems to be that the root of the
        report is nested inside a containing folder
        where the folder name is the name of the archive without an extension
            for example:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut.tar.xz

            contains a folder named:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut

            which acts as the root of the report
        so all calls to TarFile.getmember() should use this "root name" as a prefix when
        locating files to extract
        """
        _root_name = _report.with_suffix('').stem
        _file_name = "version.txt"
        _target = _root_name + "/" + _file_name

        try:
            with tarfile.open(_report) as tar: 
                """
                get the content of the _target file
                TarFile.extractfile() returns a io.BufferedReader()
                for ease of use, it can be wrapped in a io.TextIOWrapper()
                and treated like a regular file handle similar to that returned from
                open()
                    see:
                    https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile
                    https://docs.python.org/3/library/io.html#io.BufferedReader
                    https://stackoverflow.com/q/51468724
                """
                _content = io.TextIOWrapper(tar.extractfile(_target)).readline()

                if "sosreport" not in _content:
                    return False
                
        except KeyError:
            #if not found in the archive
            return False
        
        return True

    def contains_file(self, target):
        return self._contains_file(target)
    
    def _contains_file(self, target):
        """
        Check if a file is present in the sosreport
        """
        
        if self._report.is_file():
            return self._archive_contains_file(target)
        else:
            return self._dir_contains_file(target)

    def _dir_contains_file(self, target):
        _report = Path(self._report)

        _target = _report / str(target)

        if not (_target.exists()):
            return False
        
        return True

    def _archive_contains_file(self, target):
        _report = Path(self._report)

        """
        Check for 'version.txt' in the archive

        a standard pattern for sos report archives seems to be that the root of the
        report is nested inside a containing folder
        where the folder name is the name of the archive without an extension
            for example:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut.tar.xz

            contains a folder named:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut

            which acts as the root of the report
        so all calls to TarFile.getmember() should use this "root name" as a prefix when
        locating files to extract
        """
        _root_name = _report.with_suffix('').stem
        _file_name = str(target)
        _target = _root_name + "/" + _file_name

        try:
            with tarfile.open(_report) as tar: 
                """
                get the content of the _target file
                TarFile.extractfile() returns a io.BufferedReader()
                for ease of use, it can be wrapped in a io.TextIOWrapper()
                and treated like a regular file handle similar to that returned from
                open()
                    see:
                    https://docs.python.org/3/library/tarfile.html#tarfile.TarFile.extractfile
                    https://docs.python.org/3/library/io.html#io.BufferedReader
                    https://stackoverflow.com/q/51468724
                """
                tar.getmember(_target)
                return True
        except KeyError:
            #if not found in the archive
            return False

    def get_file(self, target):
        """
        Fetch the content of a file within the sosreport
        """

        if not self._contains_file(target):
            raise FileNotFoundInReport(f"Could not find this file in the sosreport: \
                                       {target}")
        
        if self._report.is_file():
            return self._archive_get_file(target)
        else:
            return self._dir_get_file(target)
    
    def _dir_get_file(self, target):
        _report = Path(self._report)

        _target = _report / str(target)

        if util.is_text(_target):
            return _target.read_text()
        return _target.read_bytes()

    def _archive_get_file(self, target):
        pass
    
"""
_report = '/home/peter/dev/sosreport-veteran-margay-test-42-2023-02-26-yevmkut'
#_report = '/home/peter/dev/sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar'
#_report = '/home/peter/dev/sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz'
_SOS = SosReport(_report)
print( _SOS.contains_file("environment") )
print( _SOS.contains_file("environment.txt") )
print( _SOS.contains_file("version.txt") )
print( _SOS.contains_file("sos_reports/sos.txt") )
print( _SOS.contains_file("sos_reports/sos") )
"""