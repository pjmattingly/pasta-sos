from pathlib import Path
_default_dir = Path.home() / ".pasta-sos"
_default_conf = _default_dir / 'config.json'

def exists():
    return _conf_exists()

def _dir_exists():
    return _default_dir.exists()

def _conf_exists():
    return _default_conf.exists()