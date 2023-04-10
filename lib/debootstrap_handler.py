'''
`debootstrap` makes chroot environments for Debian and Ubuntu systems.
The use-case for this module is to create chroot directories for older/out of date Ubuntu distros.
(more modern Ubuntu distros can be created as VMs directly)
'''

import shutil
import subprocess
import tempfile
from pathlib import Path
import os
import atexit

class Bad_Distro(Exception): pass

#keep track of the chroot created, as allowing the TemporaryDirectory object to fall out of scope, will trigger removing that directory
#_chroot = None

def is_installed():
    '''
    Check if debootstrap is installed.
    '''
    return bool(shutil.which('debootstrap'))

def make_chroot_for_distro(distro):
    '''
    Main entrypoint.
    '''
    return _make_chroot(distro)

def _make_chroot(distro, _preserve=False):
    '''
    Create temporary a chroot environment of a distribution of Ubuntu
    '''
    
    #global _chroot
    _chroot = _make_temp_dir(not _preserve)
    chroot_path = Path(_chroot.name) / str(distro) #name the chroot directory after the distro we want

    '''
    ISSUE
    debootstrap, when fetching files, will leave wget log files in the directory it's operating in
    it doesn't seem to have an option to cleanup those files
    so instead, change the excution directory before debootstrap runs, so that the log files end up
    in /tmp
    '''
    _prev = os.getcwd()
    os.chdir(Path(_chroot.name))
    
    res = subprocess.run(['sudo', 'debootstrap', '--no-check-gpg', str(distro), str(chroot_path)], capture_output=True)

    #then return to where the program was originally executed from
    os.chdir(_prev)

    if res.returncode != 0: raise Bad_Distro( f"Distribution: '{distro}' not found." )

    return str(chroot_path)

def _make_temp_dir(delete_on_program_exit=True):
    '''
    Make a temp directory that is removed on program exit.
    '''
    _dir = tempfile.mkdtemp()

    if delete_on_program_exit:
        atexit.register(lambda: shutil.rmtree(_dir, ignore_errors=True))

    return _dir