_DEBUG = False

#----
#Libs
#----

import argparse
from pathlib import Path
import os
import subprocess

import lib.debootstrap_handler as dh
import lib.util as util
import lib.lxc_handler as lh

import re

import shutil

#----
#Exceptions
#----

class Sosreport_Not_Found(Exception): pass
class Sosreport_Unreadable(Exception): pass
class Not_Sosreport(Exception): pass

class Not_Running_As_Root(Exception): pass

class Debootstrap_Not_Installed(Exception): pass
class LXC_Not_Installed(Exception): pass
class Hotsos_Not_Installed(Exception): pass

#----
#main
#----

def assert_path_ok(path):
    '''
    checking that sosreport files are usable
        see: https://docs.python.org/3/library/os.html#os.access
    '''

    sosreport = Path(path)

    if not sosreport.exists():
        raise Sosreport_Not_Found()

    if not os.access(sosreport, os.R_OK):
        raise Sosreport_Unreadable("Cannot read sosreport due to permission restrictions.")

def get_ubuntu_code_name_from_sosreport(path):
    lsb_release_a_path = Path(path) / 'sos_commands'/ 'release' / 'lsb_release_-a'

    with open(lsb_release_a_path) as f:
        content = f.read()

    #match something like: ^`Codename:       (jammy)`$
    #where we treat each line as its own string w.r.t matching (re.MULTILINE)
    return re.search(r'^Codename:\t(.+)$', content, re.MULTILINE).groups()[0]

def hotsos_is_installed(): return bool(shutil.which('hotsos'))

def assert_is_sosreport(path):
    res = subprocess.run( ['hotsos', path], capture_output=True)

    if res.returncode != 0: raise Not_Sosreport(f"This folder is not a sosreport: {path}")

if __name__ == '__main__':
    if not dh.is_installed(): raise Debootstrap_Not_Installed("Please install 'debootstrap'.")
    if not lh.is_installed(): raise LXC_Not_Installed("Please install 'lxc'.")
    if not hotsos_is_installed(): raise Hotsos_Not_Installed("Please install 'hotsos'.")
    
    #parsing CLI arguments
    parser = argparse.ArgumentParser(description='Given a sosreport from a system, create a pseudo-copy in a virtual machine.')
    parser.add_argument('sosreport', type=str, nargs=1, help='a path to a folder containing a sosreport.')
    args = parser.parse_args()

    path = Path(args.sosreport[0]).absolute()

    #check if path exists and is readable
    assert_path_ok(path)

    #check if path is actually an sosreport
    assert_is_sosreport(path)

    distro = get_ubuntu_code_name_from_sosreport(path)

    #with the distro code-name in hand, make the chroot
    #(provided it's a real distro)
    chroot_path = dh.make_chroot_for_distro(distro, _DEBUG)

    if _DEBUG: print(f"Path to tmp chroot dir: {chroot_path}")

    #set 777 on chroot to avoid re-occuring permission issues
    util.chmod_777(chroot_path)

    #then with the path to the chroot, make a compressed archive of it
    _target = Path(chroot_path).parent
    rootfs_path = util.tar_gzip(chroot_path, _target, name='rootfs')

    #also make a an archive of a metadata.yaml file for lxc
    metadata_path = util.make_metadata_yaml(distro, _target)

    '''
    ISSUE
    If an absolute path for metadata.yaml is passed to tar, then tar will reflect that path within the archive
    to avoid this issue, change the working directory to where the metadata.yaml file is and then change back after the archive is made
    '''
    _prev = os.getcwd()
    os.chdir(Path(_target))
    metadata_archive_path = util.tar_gzip(Path(metadata_path).name, _target)
    os.chdir(Path(_prev))

    #finally, import the chroot into lxc via: `lxc image import <metadata> <rootfs> --alias <name>`
    vm_name = lh.import_chroot(rootfs_path, metadata_archive_path, path.stem)

    done_message = ''
    done_message += f"Import complete, launch a container with:\n"
    done_message += f"sudo lxc launch {vm_name}"
    done_message += "\n"

    print(done_message)