import tarfile
from pathlib import Path
import os
import io

class DoesNotExist(Exception):
    pass
class NotSosReport(Exception):
    pass
class CannotRead(Exception):
    pass

class SOS:
    """
    A class symbolizing an sosreport
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
            raise NotSosReport(
                    f"Sos report should be a tar.xz archive or a directory; instead: \
                    {self._report}"
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
        where the folder name is the name of the archive without extensions
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
            with tarfile.open(_path) as tar: 
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

'''
def extractfile(file, output_dir):
    _out = Path(output_dir)

    if not ( _out.exists() and _out.is_dir() and os.access(_out, os.W_OK | os.X_OK) ):
        raise Bad_Target(f"Cannot write to '{_out.resolve()}'.")

_path = '../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz'

import tarfile
#tar = tarfile.open(_path)
'''

'''
next,

revise this class to work with sosreport folders too
rolling in all the handling and checks for sosreports in other places here

if its a dir, then extractfile() just returns the path to the file in the sosreport
folder
if its an archive, it extracts the file and points to that

then,
for extractfile
check the output_dir exists, etc.
then prepend the name of the sosreport when finding files in a sosreport archive for convenience
then return path of extracted file on success
'''

_path = '../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz'
_path = Path(_path)

"""
a standard pattern for sosreport archives seems to be that the root of the sosreport is nested inside a containing folder
where the folder name is the name of the archive without extensions
    for example:
    sosreport-veteran-margay-test-42-2023-02-26-yevmkut.tar.xz

    contains a folder named:
    sosreport-veteran-margay-test-42-2023-02-26-yevmkut

    which acts as the root of the report
so all calls to getmember() should use this "root name" as a prefix when locating
files to extract
"""
_root_name = _path.with_suffix('').stem
_file_name = "version.txt"
_target = _root_name + "/" + _file_name

try:
    with tarfile.open(_path) as tar: 
        #print(tar.getmembers())
        #print( tar.getmember("sosreport-peter-virtual-machine-2023-04-16-nqsngbd") )
        #print( tar.getmember(_target) )
        pass
except KeyError:
    raise TargetNotFound(f"Could not locate in sosreport: {_target}")

#_test_sos = SOS( '../../sosreport-veteran-margay-test-42-2023-02-26-yevmkut' )
#print( _test_sos._is_dir_sosreport('../../sosreport-veteran-margay-test-42-2023-02-26-yevmkut') )

#_test_sos = SOS( '../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar' )
#print( _test_sos._is_dir_sosreport('../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar') )

_test_sos = SOS( '../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar' )
print( _test_sos._is_archive_sosreport('../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar') )

_test_sos = SOS( '../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz' )
print( _test_sos._is_archive_sosreport('../../sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz') )

_test_sos = SOS( '../../sosreport-veteran-margay-test-42-2023-02-26-yevmkut' )
print( _test_sos._is_archive_sosreport('../../sosreport-veteran-margay-test-42-2023-02-26-yevmkut') )