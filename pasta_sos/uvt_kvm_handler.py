import shutil

def is_installed():
    return bool(shutil.which('uvt-kvm') and shutil.which('uvt-simplestreams-libvirt'))