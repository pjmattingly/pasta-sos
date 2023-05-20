# pasta-sos
Create a virtual machine from a sosreport, to allow for easier replication and troubleshooting.

## Version
v0.2.1

## Description
A common task when troubleshooting client systems is to replicate a system for testing. This may be done to isolate a bug or to attempt fixes without harming client installations. A common tool to do this is `sosreport` (see: https://github.com/sosreport/sos). `sosreport` gathers detailed information about a client's system into a single package which then can be handed off to support for the purposes of information gathering or replication. Replication is often done manually, given the information in a sosreport. This project attempts to automate the process of replication.

## Overview

At a high level this project completes several steps:

1) Read a `sosreport` and find the "friendly name" of the Ubuntu release associated with the report.
2) Use that “friendly name” with `debootstrap` to create a chroot environment of that Ubuntu release; see: https://wiki.debian.org/Debootstrap.
3) With the Ubuntu environment bootstrapped, it is then imported as an image into `lxc`; see: https://linuxcontainers.org/lxc/introduction/.

Finally, any container created from the image should be a usable Ubuntu environment whose version matches the information found in the sosreport.

Feedback on usage is appreciated, and recommendations on features and improvements are encouraged; see the discussion forum: https://github.com/pjmattingly/pasta-sos/discussions/categories/ideas.

At the moment there is no packaging associated with this project, and so the installation instructions seek to mimic a development environment.

This tool is in an alpha state and will likely break. Please use the [Issues](https://github.com/pjmattingly/pasta-sos/issues) tab for reporting.

## Install

### For running pasta-sos

0) Start installation on Ubuntu Jammy (22.04) (A freshly installed virtual machine is recommended).
1) Install `debootstrap`; `sudo apt install debootstrap`.
2) Install `lxc`; `sudo apt install lxc`.
3) Run lxc initialization; `sudo lxd init`.
4) Install `python`; `sudo apt install python3.10`; see: https://www.python.org/downloads/.
5) Install `pip`; `sudo apt install python3-pip`; see: https://pip.pypa.io/en/stable/installation/.
6) Install `poetry`; `curl -sSL https://install.python-poetry.org | python3 -`; see: https://python-poetry.org/docs/#installing-with-the-official-installer
7) Clone the repository `git clone https://github.com/pjmattingly/pasta-sos`; see: https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository.
8) Install dependencies; `poetry install`.

Then pasta-sos can be ran with: `poetry run python main.py <path/to/sosreport>`. It’s recommended to use the poetry shell for ease of use: `poetry shell` then  `python main.py <path/to/sosreport>`.

### For developing pasta-sos

(Complete the above steps to install pasta-sos)

9) Install Visual Studio Code (VSCode); `snap install code`; see: https://snapcraft.io/code.
10) Install linter/code styler Ruff; VSCode should prompt to install when opening the pasta-sos directory, otherwise: Ctrl+Shift+P and `ext install charliermarsh.ruff`.

Otherwise, if you prefer another editor, see the manual installation instruction for Ruff here: https://github.com/charliermarsh/ruff#installation.

## Running

Start by running `pasta-sos` with a path to a sosreport, note that the script will prompt for elevation with `sudo`. Running `pasta-sos` will create an image in your local lxc image store; run `lxc image list` to view. The name of the created image follows this pattern: `<name of sosreport>_<short UUID>`. To start a container from the image: `sudo lxc launch <name or fingerprint of image>`. To setup a password for the root user inside the container: `sudo lxc exec <Container name> -- sh -c "passwd"`; This should allow the user to login to the container. Attach to the container's console: `sudo lxc console <Container name>`. Once logged into the container, the user will likely need to run `dhclient` (or similar) to get an IP address; see https://manpages.ubuntu.com/manpages/jammy/man8/dhclient.8.html.

As for shutting down the container and removing the image from the lxc store, the user is encouraged to consult the lxc doucmentation: https://linuxcontainers.org/lxc/getting-started/.

## Future work

### v0.3

In this iteration we build on the work done in v0.2.0 by injecting the chroot environment into a virtual machine, rather than a container. This should provide a more realistic environment for replication.

An approach is to:

1) Make a file as a base for the image: `dd if=/dev/zero of=rootfs.img bs=1 count=0 seek=300M`.
2) Format the image ext4: `mkfs.ext4 -b <block size> -F rootfs.img`.
3) Mount the image.
3) Copy the files from the chroot environment into the image.
4) Use QEMU to format the image.
5) Import into LXC.

### v0.4+

Beyond creating a virtual machine or container, the next order of business is cloning installed packages. That is, `sosreport` gathers information about installed packages on a client machine. Thus, a means of installing (approximately) identical packages to a `pasta-sos` virtual machine would be helpful in troubleshooting difficult to reproduce issues.

Second, snapshot support. It would be very helpful to complete an installation, and automatically create a snapshot of the freshly installed virtual machine. This would allow for a user to experiment with changes and rollback to a standard known good state.

Third, support for `cloud-init`. `cloud-init` is a means for "cloud instance initialization" (https://cloudinit.readthedocs.io/en/latest/). As such, specifying packages to be added to the virtual machine produced by `pasta-sos` with `cloud-init` seems to be a reasonable approach for further duplicating the state of client systems.

Other future ideas: More human readable image names (e.g., based off case numbers). Backups. Tools for inducing rare real-world scenarios with the virtual machines (for example, packet loss, out of memory, out of storage space, etc.). Support for detecting or configuring other virtualisation back-ends (e.g., KVM). Support for the creation of networks of virtual machines to mimic complex deployments on the client-side (perhaps with k8s?). Duplication of running service configurations, given configuration files and information from a client machine. Cloning hardware configurations; For example, a client machine may have two network interfaces, and a variety of storage devices, a pasta-sos virtual machine could mimic this configuration.
