import tarfile
from pathlib import Path
import util
#import os

class DoesNotExist(Exception):
    pass
class NotFile(Exception):
    pass
class NotTar(Exception):
    pass
class TargetNotFound(Exception):
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
        self._is_archive = False

        if not ( self._report.exists() ):
            raise DoesNotExist(f"Could not find sosreport: {self._report}")
        
        if self._report.is_file():
            self._is_archive = True

        if self._is_archive():
            if not (tarfile.is_tarfile(self._report)):
                raise NotTar(
                    f"Sosporet should be a tar.xz archive or a directory; instead: \
                    {self._report}"
                    )
            
            #try to mount the archive
            #_mnt = util.make_temp_dir()


            #raise NotFile(f"This is not a file: {self._report}")

    def _is_sosreport(self, report):
        pass

    def _is_archive(self):
        return self._is_archive

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
        print( tar.getmember(_target) )
except KeyError:
    raise TargetNotFound(f"Could not locate in sosreport: {_target}")