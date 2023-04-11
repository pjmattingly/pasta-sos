# pasta-sos
Create a virtual machine from an sosreport, for troubleshooting.

## Version
v0.2.0

## Description
A common task when troubleshooting client systems is to replicate a system for testing. This is done to issolate a bug or to attempt fixes without harming client infrastructure. A common tool to do this is `sosreport` (see: https://github.com/sosreport/sos). `sosreport` gathers detailed information about a client's system into a single package which then can be handed off to support for the purposes of information gathering or replication. Replication is often done manually, given the information in a sosreport. This project attempts to automate the process of replication.

## Overview

At a high level the code proceeds through several steps:

1) Read a `sosreport` and find the "friendly name" of the Ubuntu release the `sosreport` describes.
2) Use that name with `debootstrap` to create a chroot environment of that Ubuntu release; see: https://wiki.debian.org/Debootstrap.
3) With the Ubuntu environment bootstraped, it is then imported as an image into `lxc`; see: https://linuxcontainers.org/lxc/introduction/.

Finally, any container created from the image should be a usable Ubuntu environment whose version matches the information found in the sosreport.

Note, that this project also depends on `hotsos` for parsing validating sosreports; see: https://github.com/canonical/hotsos.

Feedback on usage is appreciated, and recommendations on features and improvements are encouraged; see the discussion forum: https://github.com/pjmattingly/pasta-sos/discussions/categories/ideas.

At the moment there is no packaging associated with this project, and so the installation instructions seek to mimic a development environment.

This tool is in an alpha state and will likely break. Please use the [Issues](https://github.com/pjmattingly/pasta-sos/issues) tab for reporting.

## Install

0) Start installation on Ubuntu Jammy (22.04) (A freshly installed virtual machine is recommended)
1) Install `debootstrap`; `sudo apt install debootstrap`.
2) Install `lxc`; `sudo apt install lxc`.
3) Run lxc initialization; `sudo lxd init`.
4) Install `hotsos`; `sudo snap install hotsos --classic`; See: https://github.com/canonical/hotsos#install
5) Install `python` (with virtual environment support); `sudo apt install python3.10-venv`; see: https://www.python.org/downloads/



2) Install `multipass`; `sudo snap install multipass`; See: https://github.com/canonical/multipass#install-multipass

4) Install `pip`; `sudo apt install python3-pip`; see: https://pip.pypa.io/en/stable/installation/
5) Install `pipx`; `python3 -m pip install --user pipx` and `python3 -m pipx ensurepath`; see: https://pypi.org/project/pipx/
6) Reload the shell to make `pipx` visible (exec "$SHELL")
7) Install `pipenv`; `pipx install pipenv`; see: https://pypi.org/project/pipenv/#installation<sup>1</sup>
8) Clone the repository `git clone https://github.com/pjmattingly/pasta-sos`; see: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
9) Install dependencies `pipenv install`; see: https://pipenv-fork.readthedocs.io/en/latest/basics.html
10) Run `pipenv run python main.py <path/to/sosreport folder>`

<sup>1</sup> Note here we install with `pipx` and NOT `apt`, as installing with `apt` causes this issue: https://github.com/pypa/pipenv/issues/5088.

Note, that the installation follows this somewhat complex process to avoid a bug effecting Ubuntu Jammy (22.04) and Python 3.10 (https://github.com/pypa/pipenv/issues/5075).

## Cleanup

`pasta-sos` will create virtual machines with `multipass`. At this time there is no functionality for removing these virtual machines automatically. `pasta-sos` will report the names of the virtual machines it creates with output to STDOUT; Similar to: `Launched: <name of VM>`. Use the command `multipass delete <name of VM>` to remove the virtual machines it creates; You may also need to use `multipass purge` to remove deleted virtual machines from your system.

## Current work

### v0.2.0

In this iteration we use `deboostrap` to build chroot environments of any Ubuntu release; See: https://wiki.debian.org/Debootstrap.

This approach builds off this sequence of steps:

1) `sudo debootstrap --no-check-gpg <ubuntu release code name> <chroot directory>`
2) Modify the chroot's `sources.list` to include legacy sources: `deb http://old-releases.ubuntu.com/ubuntu <ubuntu release code name> main universe multiverse restricted`
3) Then, the environment inside the chroot directory can use `apt` normally to install packages
(for example: `sudo chroot <chroot directory> apt-get update` then `sudo chroot <chroot directory> apt-get install -y apt-file`)

Then using `apt` packages can be installed to match the configuration found in the `sosreport`.

sources:
  https://askubuntu.com/questions/1123021/the-packages-for-old-releases-are-not-available-anymore/1123049#1123049
  https://help.ubuntu.com/community/EOLUpgrades
  https://askubuntu.com/a/1123049
  https://superuser.com/a/339572

### v0.3.0

In this iteration we build on the work done in v0.2.0 by injecting the chroot environment into a virtual machine.

An approach is to:

1) Make a file as a base for the image: `dd if=/dev/zero of=rootfs.img bs=1 count=0 seek=300M`
2) Format the image `mkfs.ext4 -b <block size> -F rootfs.img`
3) Copy the files from the chroot environment into the image
4) Use QEMU to boot the image

Other possible approaches include: 

1) using Clonezilla to build the image from the chrooted environment
2) using the `virt-p2v` tool to attempt to create an image based on the chrooted environment

src:
  https://wiki.ubuntu.com/ARM/RootfsFromScratch/QemuDebootstrap
  https://en.wikipedia.org/wiki/Clonezilla
  https://manpages.ubuntu.com/manpages/jammy/man1/virt-p2v.1.html
 
## Future

I believe the first order of business cloning installed packages. That is, `sosreport` gathers information about installed packages on a client machine. Thus, a means of installing (approximately) identical packages to a `pasta-sos` virtual machine would be helpful in troubleshooting difficult to reproduce issues.<sup>1</sup>

Second, snapshot support. This should allow for easy rollbacks after making changes to the virtual machine. At this time `multipass` does not support snapshots; Though it is a promised feature for a future release: https://github.com/canonical/multipass/issues/208<sup>2</sup>. `multipass` was chosen for this initial version due to its simplicity of use. In the future, another virtual machine creation tool will be used in the place of `multipass` for future releases (e.g., libvirt, etc.).

Third, support for `cloud-init`. `cloud-init` is a means for "cloud instance initialisation" (https://cloudinit.readthedocs.io/en/latest/). As such, specifying packages to be added to the virtual machine produced by `pasta-sos` with `cloud-init` seems to be a reasonable approach for further duplicating the state of client systems.

Other future ideas: support for creating containers in addition to (or instead of?) virtual machines. Automatic cleanup of created virtual machines. Virtual machine names that include case numbers. Backups. Tools for inducing rare real-world scenarios with the virtual machines (for example, packet loss, out of memory, out of storage space, etc.). Support for a variety of "shells" that mimic the behaviour of other virtual machine management tools (e.g., lib-virt, virt-manager, uvt-kvm), to allow for ease of integration with existing solution that use different tooling; for example: `pasta-sos shell uvt-kvm`, which then causes pasta-sos to act like `uvt-kvm`. Support for the creation of networks of virtual machines to mimic complex deployments on the client-side (perhaps with k8s?). Duplication of running service configurations, given configuration files and binaries from a client machine. Cloning hardware configurations; For example, a client machine may have two network interfaces, and a variety of storage devices, a pasta-sos virtual machine should mimic this configuration.

---- 

<sup>1</sup>As pointed out by [`desrod`](https://github.com/desrod), this is startingly complex topic. A key factor in this, is that client machines may have packages that are no longer available. As such, the question becomes: how to either (1) find such packages in available archives or (2) mimic these older packages such that they can be used in a virtual machine for reproduction? Current lines of inquiry include: `equivs` (https://manpages.debian.org/testing/equivs/equivs-build.1.en.html, https://wiki.debian.org/Packaging/HackingDependencies), `lpmadison` (https://github.com/desrod/lpmadison), `apt-clone` (https://manpages.ubuntu.com/manpages/jammy/man8/apt-clone.8.html), and `Minimal Ubuntu` (https://wiki.ubuntu.com/Minimal). As well as searching for the means of "mocking" or "stubbing" such packages.

<sup>2</sup>There is technically a means of [creating snapshots manually](https://github.com/canonical/multipass/issues/208#issuecomment-910422845), given the underlying virtual machine driver. But this is likely to create edge-cases and bugs, and so moving to a different approach seems to be the best course of action.
