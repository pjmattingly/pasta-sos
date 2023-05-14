import tarfile
from pathlib import Path
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
    a sosreport can be a folder or a compressed archive (tar.xz)
    normal workflows include:
        checking that the sosreport is valid by checking for a "version.txt" file
        extracting files from the sosreport
        checking for presence of files in a sosreport
    """

    def __init__(self, report):
        self._report = Path(report)
        
        if not ( self._is_sosreport(self._report) ):
            _r = self._report
            raise NotSosReport(
                f"Sos report should be a tar.xz archive or a directory; instead: {_r}"
                )
        
    def _is_sosreport(self, report):
        """
        An sosreport always seems to contain a "version.txt" file that appears to
        be separate from the files from the target computer.
        This file contains information about the sosreport version used and so
        checking for the string "sosreport" in this file can be used as a method to 
        determine if `report` is a path to an actual sosreport.
        """
        _report = Path(report)

        if not ( util.file_exists_and_is_readable(_report) ):
            raise DoesNotExist(f"Could not access sosreport: {_report}")
        
        if ((_report.is_file() and tarfile.is_tarfile(_report))
            or
            _report.is_dir()):
            
            try:
                _content = self._get_file(report, "version.txt")
                return ("sosreport" in _content)
            except FileNotFoundInReport:
                pass
        
        return False

    def contains_file(self, target):
        return self._contains_file(self._report, target)
    
    def _contains_file(self, report, target):
        """
        Check if a file is present in the sosreport
        """
        
        try:
            self._get_file(self, report, target)
        except FileNotFoundInReport:
            return False
        return True

    def get_file(self, target):
        return self._get_file(self, self._report, target)

    def _get_file(self, report, target):
        """
        Fetch the content of a file within the sosreport
        (Assumes that `report` is a path to a readable sosreport file)
        """
        _report = Path(report)

        """
        if not self._contains_file(target):
            raise FileNotFoundInReport(f"Could not find this file in the sosreport: \
                                       {target}")
        """
        
        if _report.is_file():
            return self._archive_get_file(report, target)
        else:
            return self._dir_get_file(report, target)
    
    def _dir_get_file(self, report, target):
        """
        Return the contents of target in a diretory-style sosreport
        (Assumes that `report` is a path to a readable sosreport)
        """

        _report = Path(report)

        _target = _report / str(target)

        if not _report.exists():
            raise FileNotFoundInReport(f"Could not find this file in the sosreport: \
                                       {target}")

        if util.is_text(_target):
            return _target.read_text()
        return _target.read_bytes()

    def _archive_get_file(self, report, target):
        """
        Return the contents of target in an archive-style sosreport
        (Assumes that `report` is a path to a readable sosreport)
        """
        _report = Path(report)

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
        try:
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
        except KeyError:
            raise FileNotFoundInReport(f"Could not find this file in the sosreport: \
                                       {target}")