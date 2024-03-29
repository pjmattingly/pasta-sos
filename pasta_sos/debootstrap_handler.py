'''
`debootstrap` makes chroot environments for Debian and Ubuntu systems.
The use-case for this module is to create chroot directories for older/out of date 
Ubuntu distros.
(more modern Ubuntu distros can be created as VMs directly)
'''

import shutil
import subprocess
from pathlib import Path
import os
import pasta_sos.util as util

class BadDistro(Exception):
    pass

def is_installed():
    '''
    Check if debootstrap is installed.
    '''
    return bool(shutil.which('debootstrap'))

def make_chroot_for_distro(distro, _preserve=False):
    '''
    Main entrypoint.
    '''
    return _make_chroot(distro, _preserve)

def _make_chroot(distro, _preserve=False):
    '''
    Create temporary a chroot environment of a distribution of Ubuntu
    '''
    
    _chroot = util.make_temp_dir(not _preserve)
    
    #name the chroot directory after the distro we want
    chroot_path = Path(_chroot) / str(distro) 

    '''
    ISSUE
    debootstrap, when fetching files, will leave wget log files in the directory it's 
    operating in
    it doesn't seem to have an option to cleanup those files
    so instead, change the excution directory before debootstrap runs, so that the log
    files end up in /tmp
    '''
    _prev = os.getcwd()
    os.chdir(Path(_chroot))
    
    _c = ['sudo', 'debootstrap', '--no-check-gpg', str(distro), str(chroot_path)]
    res = subprocess.run(_c, capture_output=True)

    #then return to where the program was originally executed from
    os.chdir(_prev)

    if res.returncode != 0:
        raise BadDistro( f"Distribution: '{distro}' not found." )

    return str(chroot_path)