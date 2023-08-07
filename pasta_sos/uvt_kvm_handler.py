import shutil

class UvtNotInstalled(Exception):
    def __init__(self):
        m = "Please install 'uvtool': `sudo apt -y install uvtool`."
        
        super().__init__(m)

def is_installed():
    return bool(shutil.which('uvt-kvm') and shutil.which('uvt-simplestreams-libvirt'))