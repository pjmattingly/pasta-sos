import os
import psutil
from pathlib import Path

def is_key_on_system(key):
    _key = str(key).strip()

    for pub in _get_public_keys():
        _local_key = Path(pub).read_text().strip()

        if _key == _local_key:
            return True
    return False 

def _get_public_keys():
    return [file for file in (Path.home() / ".ssh").glob('**/*.pub')]