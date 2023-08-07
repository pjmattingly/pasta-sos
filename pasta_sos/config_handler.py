from pathlib import Path
_default_loc = Path.home() / ".pasta-sos" / 'config.json'

def exists():
    return _default_loc.exists()