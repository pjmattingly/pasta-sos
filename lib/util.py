'''
Compress a directory and return a path to the produced file
    throwing on not found, etc.
`sudo tar -cvzf rootfs.tar.gz -C precise_chroot .`
'''
import tarfile
from pathlib import Path
import os

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
    if not ( _out.exists() and _in.is_dir() and os.access(_out, os.W_OK | os.X_OK) ): raise Bad_Target(f"Cannot write rootfs to '{_out.resolve()}'.")

    _out = _out / "rootfs.tar.gz"

    with tarfile.open(_out, "w:gz") as tar:
        #add the contents of the target directory to the root of the tar file
        #see: https://stackoverflow.com/questions/2032403/how-to-create-full-compressed-tar-file-using-python#comment72978579_17081026
        tar.add(_in, arcname='/')

    return str(_out.resolve())