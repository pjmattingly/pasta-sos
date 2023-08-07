from pathlib import Path
import shelve

_default_dir = Path.home() / ".pasta-sos"
_defalt_name = 'config'
_default_conf = _default_dir / _defalt_name

def exists():
    return _conf_exists()

def _dir_exists():
    return _default_dir.exists()

def _conf_exists():
    return _default_conf.exists()

def _check_setup():
    if not _dir_exists():
        _default_dir.mkdir()
    
    #if not _conf_exists():
    #    _default_conf.touch()

def add(key, value):
    return _add(key, value)

def _add(key, value):
    _check_setup()
    with shelve.open(str(_default_conf)) as db:
        db[key] = value

def dell(key):
    return _del(key)

def _del(key):
    _check_setup()
    with shelve.open(str(_default_conf)) as db:
        del db[key]

def add_LaunchPad_username(value):
    return _add("Launchpad_username", value)