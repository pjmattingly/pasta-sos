#!/bin/bash

# configure remote
if ! lxc remote ls | grep -q slapstack; then
	lxc remote add slapstack 10.230.69.53 --public
	lxc profile create ad-profile
fi

# select version
VER="$1"
if [ "$VER" != "2k19" ]; then
	VER=2k22
fi

# server setup
echo '|-----------------------------------------------------|'
echo "| Deploying Windows Server $VER with Active Directory |"
echo '|-----------------------------------------------------|'

if lxc image ls local: | grep -q win"$VER"; then
	REPO=local
else
	REPO=slapstack
fi

lxc launch ${REPO}:win"$VER" win"$VER" -c limits.cpu=2 -c limits.memory=6GB --vm

echo 'Waiting for Windows (as usual)...'

while [ -z $IP ]; do
	IP=$(lxc ls -c n4 -f compact | grep win"$VER" | awk '{print $2}')
done

# client setup
echo '|-------------------------------------------|'
echo '| Deploying Ubuntu 22.04 LTS client machine |'
echo '|-------------------------------------------|'
echo "config:
  cloud-init.user-data: |
    #cloud-config
    package_update: true
    package_upgrade: true
    packages:
      - sssd-ad
      - sssd-tools
      - realmd
      - adcli
      - samba-common-bin
      - policykit-1
      - packagekit
    runcmd:
      - echo \"DNS=$IP\" >> /etc/systemd/resolved.conf
      - echo \"[libdefaults]\ndefault_realm = EXAMPLE.COM\nrdns = false\" > /etc/krb5.conf
      - systemctl restart systemd-resolved
      - echo 'Passw0rd' | realm join example.com
      - pam-auth-update --enable mkhomedir
      - echo 'ad_gpo_access_control = disabled' >> /etc/sssd/sssd.conf
      - systemctl restart sssd
description: AD-Joined Computer" | lxc profile edit ad-profile
lxc launch images:ubuntu/jammy/cloud ad-client -p default -p ad-profile

echo -e "Configuring the client with cloud-init..."

until lxc exec ad-client id test1@example.com &> /dev/null
do
	sleep 2
done

# final checks
echo
echo "DOMAIN INFO:"
lxc exec ad-client realm list
echo
echo "TEST USER LOOKUP:"
lxc exec ad-client id test1@example.com
echo
echo '|----------------------|'
echo "| Deployment Complete! |"
echo '|----------------------|'
lxc ls -c n4st -f compact | grep 'NAME\|win2k\|ad-client'
echo
echo 'Password for all AD accounts: Passw0rd'
