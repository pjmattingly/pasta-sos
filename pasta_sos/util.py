'''
Compress a directory and return a path to the produced file
    throwing on not found, etc.
`sudo tar -cvzf rootfs.tar.gz -C precise_chroot .`
'''
import tarfile
from pathlib import Path
import os
import time
import subprocess
import tempfile
import atexit
import shutil

class Bad_Input(Exception): pass
class Bad_Target(Exception): pass

class Chmod_Error(Exception): pass

def tar_gzip(source, output_dir, **kwargs):
    '''
    Given a file or directory, create a compressed archive (tar.gz) of it in output_dir
    see: https://stackoverflow.com/a/17081026
    '''
    _in = Path(source)
    _out = Path(output_dir)

    if not ( _in.exists() ):
        raise Bad_Input(f"Could not compress '{_in.resolve()}'.")
    if not ( _out.exists() and _out.is_dir() and os.access(_out, os.W_OK | os.X_OK) ):
        raise Bad_Target(f"Cannot write to '{_out.resolve()}'.")

    if "name" in kwargs:
        _out = _out / f"{kwargs['name']}.tar.gz"
    else:
        _out = _out / f"{_in.name}.tar.gz"

    with tarfile.open(_out, "w:gz") as tar:
        if _in.is_dir():
            # if _in is a directory, then use this special form to recursively add the 
            # dir to the root of the tar file
            # see: https://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python#comment72978579_17081026
            tar.add(_in, arcname='/')
        else: 
            #otherwise, normal handling for a single file
            tar.add(_in)

    return str(_out.resolve())

def make_metadata_yaml(distro, output_dir):
    '''
    Create a metadata.yaml file for lxc, and return the path to the file
    '''

    _out = Path(output_dir)
    if not ( _out.exists() and _out.is_dir() and os.access(_out, os.W_OK | os.X_OK) ): raise Bad_Target(f"Cannot write to '{_out.resolve()}'.")
    
    _content = f'''
    architecture: "x86_64"
    creation_date: {time.time()}
    properties:
    architecture: "x86_64"
    description: "Automatically generated install of '{distro}' by pasta-sos."
    os: "ubuntu"
    release: "{distro}"
    '''

    _cleaned_content = "\n".join([line.strip() for line in _content.strip().split("\n")])
    
    _out_file = _out / 'metadata.yaml'
    _out_file.write_text(_cleaned_content)

    return str(_out_file.resolve())

def chmod_777(target):
    '''
    Given a path to a file, recursively `chmod` it to full read, write, and execute permissions
    (this is used to address annoying permission issues with the output of debootstrap, etc.)
    '''

    _in = Path(target)
    if not ( _in.exists() ): raise Bad_Input(f"Could not find: '{_in.resolve()}'.")

    res = None
    if _in.is_file():
        res = subprocess.run(['sudo', 'chmod', '777', str(_in.resolve())], capture_output=True)

    if _in.is_dir():
        res = subprocess.run(['sudo', 'chmod', '-R', '777', str(_in.resolve())], capture_output=True)

    if res.returncode != 0: raise Chmod_Error(f"Cannot change permissions on: {_in}; Giving up.")

def make_temp_dir(delete_on_program_exit=True):
    '''
    Make a temp directory that is (usually) removed on program exit.
    '''
    _dir = tempfile.mkdtemp()

    if delete_on_program_exit:
        atexit.register(lambda: shutil.rmtree(_dir, ignore_errors=True))

    return _dir