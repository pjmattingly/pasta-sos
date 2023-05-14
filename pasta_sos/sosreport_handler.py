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
        
        if not ( self._is_sosreport(self._report) ):
            _r = self._report
            raise NotSosReport(
                f"Sos report should be a tar.xz archive or a directory; instead: {_r}"
                )
        
    def _is_sosreport(self, report):
        _report = Path(report)

        if not ( util.file_exists_and_is_readable(_report) ):
            raise DoesNotExist(f"Could not access sosreport: {_report}")
        
        if ((_report.is_file() and tarfile.is_tarfile(_report))
            or
            self._report.is_dir()):
            
            # TODO? refactor here to only try to fetch the file, and look for
            # FileNotFoundInReport to indicate file isn't found?
            
            if self._contains_file("version.txt"):
                _content = self._get_file(self, "version.txt")
                return ("sosreport" in _content)
        
        return False
        

        """
        return 

        if _report.is_file():
            return self._is_archive_sosreport(report)
        else:
            return self._is_dir_sosreport(report)
        """

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

    #TODO, change these internal methods to take an argument of a report, rather
    #than getting it off `self`
    def _dir_contains_file(self, target):
        _report = Path(self._report)

        _target = _report / str(target)

        if not (_target.exists()):
            return False
        
        return True

    def _archive_contains_file(self, target):
        _report = Path(self._report)

        """
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
        return self._get_file(self, target):

    def _get_file(self, target):
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
        """
        Return the content of a file within an sosreport report archive as either
        a string or as a bytes-object; depending on file-type.
        """
        _report = Path(self._report)

        """
        a standard pattern for sos report archives seems to be that the root of the
        report is nested inside a containing folder
        where the folder name is the name of the archive without an extension
            for example:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut.tar.xz

            contains a folder named:
            sosreport-veteran-margay-test-42-2023-02-26-yevmkut

            which acts as the root of the report
        so all calls to TarFile.extractfile() should use this "root name" as a prefix 
        when locating files to extract
        """
        _root_name = _report.with_suffix('').stem
        _file_name = str(target)
        _target = _root_name + "/" + _file_name
        
        """
        BUG?

        The documentation from TarFile.extractfile claims that "If member is a regular 
        file or a link, an io.BufferedReader object"
        This is not the case, as during testing an `ExFileObject` is returned instead
        It's not clear what this file type is, as it's not listed in the documentation
        for 3.10.
        However, this thread implies that the object may be associated with the
        TarFile class in Python 3; Implying that it was a part of the class prior
        to 3.5 (as far back as the docs go)?
            see:
            https://github.com/pandas-dev/pandas/issues/16530
        There are other documentations for "stdlib" Python that show this class,
        but nothing in the main documentation.
            see:
            https://epydoc.sourceforge.net/stdlib/tarfile.ExFileObject-class.html
            https://tedboy.github.io/python_stdlib/generated/generated/tarfile.ExFileObject.html#tarfile.ExFileObject
        """
        with tarfile.open(_report) as tar:
            """
            BUG
            When completing this read with the form:
            
            ```
            tar = tarfile.open(_report)
            _content = tar.extractfile(_target)
            _data = _content.read()
            _content.close()
            tar.close()
            return _data
            ```

            The content of the opened file is truncated. This issue is resolved
            when using the `with` pragma instead.
            """
            _content = tar.extractfile(_target).read()

            try:
                #checking if _content is text, if so then return its decode() value
                return _content.decode()
            except UnicodeDecodeError:
                #otherwise content is bytes, so just return it raw
                return _content

#_report = '/home/peter/dev/sosreport-veteran-margay-test-42-2023-02-26-yevmkut'
#_report = '/home/peter/dev/sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar'
_report = '/home/peter/dev/sosreport-peter-virtual-machine-2023-04-16-nqsngbd.tar.xz'
_SOS = SosReport(_report)

res = _SOS._archive_get_file('usr/share/zoneinfo/America/Edmonton')
#res = _SOS._archive_get_file('version.txt')
#res = _SOS._archive_get_file('sos_logs/sos.log')

print(res)