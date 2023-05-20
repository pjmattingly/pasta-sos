'''
check if lxc/lxd is installed

then, given a compressed rootfs, create a container from it
'''

import shutil
import subprocess
import shortuuid

class LXCError(Exception):
    pass

def is_installed():
    '''
    Check if debootstrap is installed.
    '''
    return bool(shutil.which('lxc'))

def import_chroot(rootfs, metadata, vm_name):
    '''
    Given a rootfs.tar.gz, a metadata.yaml.tar.gz, and a name for the VM
    import them with lxc to create a container, and return the name of the container
    '''
    
    _name = f"{vm_name}_{shortuuid.ShortUUID().random(length=5)}"

    _c = ['sudo', 'lxc', 'image', 'import', str(metadata), str(rootfs), '--alias', 
          str(_name)]
    res = subprocess.run(_c, capture_output=True)

    if res.returncode != 0:
        raise LXCError(res.stderr.decode())
    
    return _name