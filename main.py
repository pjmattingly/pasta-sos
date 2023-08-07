import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError
import json

import pasta_sos.util as util

class UvtNotInstalled(Exception):
    pass

class LaunchpadUsernameNotExist(Exception):
    pass

class UnexpectedError(Exception):
    pass

def is_uvt_installed():
    return bool(shutil.which('uvt-kvm') and shutil.which('uvt-simplestreams-libvirt'))

def has_config():
    return (Path('~/.pasta-sos').exists() and Path('~/.pasta-sos/config.json').exists())

def promt_for_Launchpad_username():
    #see: https://docs.python.org/dev/library/functions.html#input
    return input("Please enter a Launchpad username: ")

def create_pasta_sos_dir():
    _config_dir = Path.home() / ".pasta-sos"
    if not _config_dir.exists():
        _config_dir.mkdir()

def setup_config_file():
    _config_dir = Path.home() / ".pasta-sos"
    if not _config_dir.exists():
        m = f"Was expecting config dir, but could not find: {_config_dir}."
        raise UnexpectedError(m)
    
    _config_file = _config_dir / "config.json"
    if _config_file.exists():
        raise UnexpectedError(f"Was not expecting config file to exist: {_config_file}")
    
    _config_file.touch()
    
    return _config_file

def add_LaunchPad_username_to_config(username, config_path):
    with open(config_path, "w") as f:
        json.dump({"Launchpad_username" : username}, f)

if __name__ == "__main__":
    if not is_uvt_installed():
        raise UvtNotInstalled("Please install 'uvtool': `sudo apt -y install uvtool`")
    
    if not has_config():
        lp_username = promt_for_Launchpad_username()

        #if not launchpad_username_exists(lp_username):
        if not util.launchpad_username_exists(lp_username):
            #see: https://stackoverflow.com/questions/10660435/how-do-i-split-the-definition-of-a-long-string-over-multiple-lines
            m = f"Could not find an active launchpad username: {lp_username}. "
            m += f"Please check that 'https://launchpad.net/~{lp_username}' "
            m+= "exists and is responding."
            raise LaunchpadUsernameNotExist(m)
        
        create_pasta_sos_dir()
        config_file_path = setup_config_file()
        add_LaunchPad_username_to_config(lp_username, config_file_path)