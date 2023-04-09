#----
#Libs
#----

import argparse
from pathlib import Path
import os
import subprocess
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
class Sosreport_Error(Exception): pass

class Not_Running_As_Root(Exception): pass

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

'''
def get_version_number_from_sosreport(path):
    sosreport = Path(path)

    #given a path to a sosreport, extract the version number from <sosreport path>/lsb-release
    p_lsb_release = sosreport / "lsb-release"

    with open(p_lsb_release) as f:
        version_string = f.read()

    words = re.split(r"\s", version_string.strip())

    #source: https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
    version_num = [i for i in filter( lambda x: bool(re.search(r'\d', x)), words )][0]

    #multipass only supports launching VMs using the major and minor version number
    #so only return the first two numbers
    #e.g., if lsb_release shows `22.04.1`, then use `22.04` to attempt to launch
    #https://en.wikipedia.org/wiki/Software_versioning

    #return ".".join(version_num.split(".")[:2])
    return version_num
'''

'''
def check_done(res):
    if res.returncode == 0:
        launched_message = re.search(r"Launched\: (.+)", res.stdout.decode()).group()
        print( launched_message )

        sys.exit(0)
'''

if __name__ == '__main__':
    assert_running_as_root()
    
    #parsing CLI arguments
    parser = argparse.ArgumentParser(description='Given a sosreport from a system, create a pseudo-copy in a virtual machine.')
    parser.add_argument('sosreport', type=str, nargs=1, help='a path to a folder containing a sosreport.')
    args = parser.parse_args()

    sosreport_path = str(Path(args.sosreport[0]).absolute())

    #check if sosreport exists and is readable
    sosreport_path_check(sosreport_path)

    #check if actually an sosreport


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