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

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import re
import sys

#----
#Exceptions
#----

class Sosreport_Not_Found(Exception): pass
class Sosreport_Unreadable(Exception): pass
class Not_Sosreport(Exception): pass

class Not_Running_As_Root(Exception): pass

class Debootstrap_Not_Installed(Exception): pass
class LXC_Not_Installed(Exception): pass

class Unknown_Error(Exception): pass

#----
#main
#----

def sosreport_path_check(path):
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

def assert_running_as_root():
    '''
    Check if running with root or root-like priviledges
        see:
        https://serverfault.com/questions/16767/check-admin-rights-inside-python-script
        https://stackoverflow.com/questions/2806897/what-is-the-best-way-for-checking-if-the-user-of-a-script-has-root-like-privileg
    '''
    if not os.environ.get("SUDO_UID") and os.geteuid() != 0: raise Not_Running_As_Root("Please run with root priviledges.")

def assert_is_sosreport(path):
    res = subprocess.run( ['hotsos', path], capture_output=True)

    if res.returncode != 0: raise Not_Sosreport(f"This folder is not a sosreport: {path}")

if __name__ == '__main__':
    assert_running_as_root()
    if not dh.is_installed(): raise Debootstrap_Not_Installed("Please install 'debootstrap' such that the root user can run it.")
    if not lh.is_installed(): raise LXC_Not_Installed("Please install 'lxc' such that the root user can run it.")
    
    #parsing CLI arguments
    parser = argparse.ArgumentParser(description='Given a sosreport from a system, create a pseudo-copy in a virtual machine.')
    parser.add_argument('sosreport', type=str, nargs=1, help='a path to a folder containing a sosreport.')
    args = parser.parse_args()

    path = str(Path(args.sosreport[0]).absolute())

    #check if path exists and is readable
    sosreport_path_check(path)

    #check if path is actually an sosreport
    assert_is_sosreport(path)

    distro = get_ubuntu_code_name_from_sosreport(path)

    #with the distro code-name in hand, make the chroot
    #(provided it's a real distro)
    chroot_path = dh.make_chroot_for_distro(distro)

    #then with the path to the chroot, make a compressed archive of it
    _target = Path(chroot_path).parent
    archive_path = util.tar_gzip(chroot_path, _target)

    #also make a an archive of a metadata.yaml file for lxc
    metadata_archive_path = util.tar_gzip(util.make_metadata_yaml(distro, _target), _target)

    print(archive_path)
    print(metadata_archive_path)
















    #code_name = get_ubuntu_code_name_from_sosreport(sosreport_path)

    #print(code_name)

    #version_num = get_version_number_from_sosreport(sosreport_path)

    #print( version_num )

    #hotsos_out = run_hotsos(sosreport_path)

    #friendly_version_name = get_version_name_from_hotsos(hotsos_out)

    #first attempt to launch VM based on version information (friendly distro name; e.g., jammy) from hotsos
    #res = run_multipass(friendly_version_name)

    #check_done(res)

    #the friendly distro name from hotsos could not be used to launch a VM (e.g., the distro name was not found amongst multipass's known images)
    #second attempt to launch VM, this time pulling version number from the sosreport
    
    #res = run_multipass(version_num)

    #check_done(res)

    #if the VM could not be launched, then error out
    #raise Unknown_Error(f"Could not launch VM based on sosreport at: '{sosreport_path}'.")