#!/usr/bin/env python

import argparse
import os

import pasta_sos.debootstrap_handler as dh
import pasta_sos.util as util
import pasta_sos.lxc_handler as lh
from pasta_sos.sosreport_handler import SosReport

import pasta_sos.exceptions as exp
from pathlib import Path

if __name__ == '__main__':
    if not dh.is_installed():
        raise exp.DebootstrapNotInstalled("Please install 'debootstrap'.")
    if not lh.is_installed():
        raise exp.LxcNotInstalled("Please install 'lxc'.")

    # parsing CLI arguments
    parser = argparse.ArgumentParser(
        description='Given a sosreport from a system, create a pseudo-copy in a \
            virtual machine.')
    parser.add_argument('sosreport', type=str, nargs=1, help='a path to a folder \
                        containing a sosreport.')
    parser.add_argument('--debug', action='store_true', help='add debug output')
    parser.add_argument('-v', '--verbose', action='store_true', help='add verbosity')
    args = parser.parse_args()

    path = Path(args.sosreport[0]).absolute()

    #load the sosreport
    sos = SosReport(path)

    #get the distro name form the sosreport
    distro = sos.ubuntu_code_name()

    # with the distro code-name in hand, make the chroot
    # (provided it's a real distro)
    chroot_path = dh.make_chroot_for_distro(distro, args.debug)

    if args.debug:
        print(f"Path to tmp chroot dir: {chroot_path}")

    # set 777 on chroot to avoid recurring permission issues
    util.chmod_777(chroot_path)

    # then with the path to the chroot, make a compressed archive of it
    _target = Path(chroot_path).parent
    rootfs_path = util.tar_gzip(chroot_path, _target, name='rootfs')

    # also make an archive of a metadata.yaml file for lxc
    metadata_path = util.make_metadata_yaml(distro, _target)

    '''
    ISSUE
    If an absolute path for metadata.yaml is passed to tar, then tar will reflect that 
        path within the archive
    to avoid this issue, change the working directory to where the metadata.yaml file is
      and then change back after the archive is made
    '''
    _prev = os.getcwd()
    os.chdir(Path(_target))
    metadata_archive_path = util.tar_gzip(Path(metadata_path).name, _target)
    os.chdir(Path(_prev))

    # finally, import the chroot into lxc via: 
    # `lxc image import <metadata> <rootfs> --alias <name>`
    vm_name = lh.import_chroot(rootfs_path, metadata_archive_path, path.stem)

    done_message = "\n".join(
        (
            '\nImport complete, launch a container with:',
            f'sudo lxc launch {vm_name}\n'
        )
    )

    print(done_message)
