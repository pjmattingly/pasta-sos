'''
`debootstrap` makes chroot environments for Debian and Ubuntu systems.
The use-case for this module is to create chroot directories for older/out of date Ubuntu distros.
(more modern Ubuntu distros can be created as VMs directly)
'''

import shutil
import subprocess
import tempfile
from pathlib import Path

class Bad_Distro(Exception): pass

#keep track of the chroot created, as allowing the TemporaryDirectory object to fall out of scope, will trigger removing that directory
_chroot = None 

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

def _make_chroot(distro):
    '''
    Create temporary a chroot environment of a distribution of Ubuntu
    '''
    
    global _chroot
    _chroot = tempfile.TemporaryDirectory()
    chroot_path = str(Path(_chroot.name))
    
    res = subprocess.run(['sudo', 'debootstrap', '--no-check-gpg', str(distro), chroot_path], capture_output=True)

    if res.returncode != 0: raise Bad_Distro( f"Distribution: '{distro}' not found." )

    return chroot_path

def _modify_chroot_sources_list(chroot_path, distro):
    '''
    Modify the sources.list of a chroot environment (at `path`) to point to `old-releases.ubuntu.com`
    We do this so that the chroot environments can pull packages that are appropriate for their older environments
        see:
        https://askubuntu.com/questions/1123021/the-packages-for-old-releases-are-not-available-anymore/1123049#1123049

    as of `debootstrap 1.0.126+nmu1ubuntu0.2` the sources.list of generated chroot for older releases seems to be set to `old-releases.ubuntu.com` correctly
    while chroot directories for more modern distros are correctly set to `archive.ubuntu.com` as well
    '''
    
    '''
    sources_list_path = Path(chroot_path) / "etc" / "apt" / "sources.list"
    '''

make_chroot_for_distro("hardy")