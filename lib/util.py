'''
Compress a directory and return a path to the produced file
    throwing on not found, etc.
`sudo tar -cvzf rootfs.tar.gz -C precise_chroot .`
'''
import tarfile
from pathlib import Path
import os
import time

class Bad_Input(Exception): pass
class Bad_Target(Exception): pass

def tar_gzip(source_dir, output_dir):
    '''
    Given a directory, create a compressed archive of that directory named "rootfs.tar.gz" in output_dir
    see: https://stackoverflow.com/a/17081026
    '''
    _in = Path(source_dir)
    _out = Path(output_dir)

    if not ( _in.exists() and _in.is_dir() ): raise Bad_Input(f"Could not compress '{_in.resolve()}' into a rootfs archive.")
    if not ( _out.exists() and _out.is_dir() and os.access(_out, os.W_OK | os.X_OK) ): raise Bad_Target(f"Cannot write to '{_out.resolve()}'.")

    _out = _out / "rootfs.tar.gz"

    with tarfile.open(_out, "w:gz") as tar:
        #add the contents of the target directory to the root of the tar file
        #see: https://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python#comment72978579_17081026
        tar.add(_in, arcname='/')

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

    return(_out_file)