# Active Directory Integration (with LXD)
This script will spin up a complete Windows AD setup with one domain-joined Ubuntu (Jammy) client. This tool differs from `../ad-sssd` in that it uses a real-life Windows Server (2019 or 2022) instead of Samba to act as the domain controller. 

**Requirements**
- Connected to Canonical VPN (to get Windows Server image)
- LXD installed with a default profile that specifies root disk and network parameters (a fresh install of LXD will work!)

# Quickstart
```
bash setup.sh [2k19|2k22]
```
Just run the setup script and the envionrment will be deployed after 10-15 minutes. Most of the setup time is due to the slow copy speed of the image from stsstack. The script will confirm the names and IP addresses of the Windows and Ubuntu instances once it completes.

Version selection is optional. If not specified, the 2k22 image is used.

# BYOAD

The `ad-profile.yaml` is the LXD profile used to deploy the client machine and is included as a separate file here for completeness. If you already have your own AD server running, this profile can be used separately to quick-deploy clients. The only thing that must be set in it is the IP of the AD server in this line:

```
      - echo "DNS=<Windows IP here!>" >> /etc/systemd/resolved.conf
```

# Clean Up
It is best to just delete the virtual instances, but removing everything is as simple as:
```
lxc rm -f ad-client win2k<19|22>
lxc profile rm ad-profile
lxc remote rm slapstack
lxc image rm $(lxc image ls -f csv | grep active-directory-se-reproducer | awk -F, '{print $2}')
```
