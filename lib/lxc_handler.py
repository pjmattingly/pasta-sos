'''
check if lxc/lxd is installed

then, given a compressed rootfs, create a container from it
'''

import shutil

def is_installed():
    '''
    Check if debootstrap is installed.
    '''
    return bool(shutil.which('lxc'))