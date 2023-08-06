import shutil

class UvtNotInstalled(Exception):
    pass

def is_uvt_installed():
    return bool(shutil.which('uvt-kvm') and shutil.which('uvt-simplestreams-libvirt'))

if __name__ == "__main__":
    if not is_uvt_installed():
        raise UvtNotInstalled("Please install 'uvtool': `sudo apt -y install uvtool`")
    
    