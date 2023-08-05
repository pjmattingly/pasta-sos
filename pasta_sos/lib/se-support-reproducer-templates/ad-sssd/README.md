## Problem description
Testing a Microsoft Active Directory connection through SSSD sometimes requires a real machine behaving as the Active Directory Domain Controller (dc), but building one using Microsoft's own tooling can be complex and non-free. 


## Solution
This KB will describe how to configure Ubuntu 20.04 as a Samba 4 server in the role of an AD DC for use in testing/configuring SSSD or similar authentication and authorization components for STS Support team members. 

## sync images for use with uvt-kvm
```
uvt-simplestreams-libvirt --verbose sync --source http://cloud-images.ubuntu.com/daily release=bionic arch=amd64
uvt-simplestreams-libvirt --verbose sync --source http://cloud-images.ubuntu.com/daily release=focal arch=amd64
```

Put the following into a shell script. I called this one build.sh: 
```
#!/bin/bash 
# set for debugging
# set -x 

os_series=bionic

# These CANNOT be greater than 15 characters because of netbios limits
server_hostname=ad-server
client_hostname=ad-client

krb5_domain=STS
sssd_realm=STS.TEST

# Could use ${sssd_realm,,} to lowercase the above if same as dns_domain
dns_domain=sts.test

passwd=$(mkpasswd --method=SHA-512 --rounds=4096 ubuntu)
# krb5_passwd=$(openssl rand -base64 12)
krb5_passwd=S3cret,P4ss
ssh_pubkey=$(< ~/.ssh/samba-dc.pub)

uvt_opts=('arch=amd64' '--memory 8192' '--cpu 2' '--disk 10')

# Generate template for the server
sed "s|ssh_pubkey|$ssh_pubkey|; \
     s|user_passwd|$passwd|; \
     s|dns_domain|$dns_domain|; \
     s|sssd_realm|$sssd_realm|g; \
     s|server_hostname|$server_hostname|g; \
     s|krb5_passwd|$krb5_passwd|; \
     s|krb5_domain|$krb5_domain|" sssd-server.tmpl > sssd-server.yaml
uvt-kvm create "$server_hostname" release=$os_series ${uvt_opts[@]} --user-data sssd-server.yaml

echo -n 'Waiting for server IP address...'
while true; do
  # Loop until the IP for the server is assigned, we need it below

  sleep 1
  if uvt-kvm ip $server_hostname 2>/dev/null; then
    # Generate template for the client
    sed "s|ad_server_ip|$(uvt-kvm ip ad-server)|; \
         s|ssh_pubkey|$ssh_pubkey|; \
         s|user_passwd|$passwd|; \
         s|dns_domain|$dns_domain|; \
         s|sssd_realm|$sssd_realm|g; \
         s|server_hostname|$server_hostname|g; \
         s|client_hostname|$client_hostname|g" sssd-client.tmpl > sssd-client.yaml
    uvt-kvm create "$client_hostname" release=$os_series ${uvt_opts[@]} --user-data sssd-client.yaml
    break
  fi
done

echo -e "In a few moments, you can ssh to the client with:\n  " \
"ssh -i ~/.ssh/samba-dc ubuntu@\$(uvt-kvm ip $client_hostname)"

printf "Your password for the Administrator account is: $krb5_passwd"
```

Create two separate .tmpl files, one called 'sssd-server.tmpl' and another called 'sssd-client.tmpl'. 

Here is sssd-server.tmpl. It's CRITICAL that the first line of these .tmpl files contain the #cloud-config starting marker: 

```
#cloud-config
no-log-init: true
preserve_hostname: false
fqdn: server_hostname.dns_domain
hostname: server_hostname
users:
  - default
  - name: ubuntu
    gecos: Ubuntu User
    primary_group: ubuntu
    groups: users
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: user_passwd
    ssh_authorized_keys:
      - ssh_pubkey
packages:
  - crudini
  - debconf-utils
  - krb5-kdc
  - libnss-winbind
  - libpam-krb5
  - libpam-winbind
  - net-tools
  - openssh-server
  - samba
  - smbclient
  - winbind
write_files:
  - path: "/tmp/krb5-config.debconf"
    permissions: "0644"
    owner: "root"
    content: |
      krb5-config     krb5-config/add_servers_realm   string sssd_realm
      krb5-config     krb5-config/default_realm       string sssd_realm
      krb5-config     krb5-config/read_conf           boolean true
  - path: "/tmp/post-install.sh"
    permissions: "0755"
    owner: "root"
    # Because these aren't in DNS, we stuff in the IPs manually, but we can't
    # do it with variables here, because the DHCP IP isn't known yet, so must
    # execute it inside the booted, networked machine
    content: |
      #!/bin/bash
      echo '127.0.0.1 localhost' > /etc/hosts
      echo "$(hostname -I)  $(hostname) $(hostname).dns_domain" >> /etc/hosts
runcmd:
  - [/tmp/post-install.sh]
  - [mv, /etc/samba/smb.conf, /etc/samba/smb.conf.orig]
  - [mv, /etc/krb5.conf, /etc/krb5.conf.orig]
  - [debconf-set-selections, /tmp/krb5-config.debconf]
  - [dpkg-reconfigure, -fnoninteractive, krb5-config]
  - [samba-tool, domain, provision, --use-rfc2307, --realm=sssd_realm, --domain=krb5_domain, "--adminpass=krb5_passwd"]
  - [systemctl, mask, smbd, nmbd, winbind]
  - [systemctl, disable, smbd, nmbd, winbind]
  - [systemctl, stop, smbd, nmbd, winbind]
  - [systemctl, unmask, samba-ad-dc]
  - [systemctl, start, samba-ad-dc]
  - [systemctl, enable, samba-ad-dc]
  - [cp, /var/lib/samba/private/krb5.conf, /etc]
  - [systemctl, stop, systemd-resolved.service]
  - [systemctl, disable, systemd-resolved.service]
  - [systemctl, restart, samba-ad-dc]
```

Here is the template for the client. Again, do not remove that first line, or this will not be parsed by cloud-init: 

```
#cloud-config
no-log-init: true
preserve_hostname: false
fqdn: client_hostname.dns_domain
hostname: client_hostname
users:
  - default
  - name: ubuntu
    gecos: Ubuntu User
    primary_group: ubuntu
    groups: users
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: user_passwd
    ssh_authorized_keys:
      - ssh_pubkey
packages:
  - adcli
  - debconf-utils
  - krb5-user
  - libnss-sss
  - libpam-sss
  - openssh-server
  - packagekit
  - realmd
  - samba-common
  - sssd
  - sssd-tools
write_files:
  - path: "/tmp/krb5-config.debconf"
    permissions: "0644"
    owner: "root"
    content: |
      krb5-config     krb5-config/add_servers_realm   string sssd_realm
      krb5-config     krb5-config/default_realm       string sssd_realm
      krb5-config     krb5-config/read_conf           boolean true
  - path: "/tmp/post-install.sh"
    permissions: "0755"
    owner: "root"
    # Because these aren't in DNS, we stuff in the IPs manually, but we can't
    # do it with variables here, because the DHCP IP isn't known yet, so must
    # execute it inside the booted, networked machine
    content: |
      #!/bin/bash
      echo '127.0.0.1 localhost' > /etc/hosts
      echo "ad_server_ip  server_hostname server_hostname.dns_domain" >> /etc/hosts
      echo "$(hostname -I)  $(hostname) $(hostname).dns_domain" >> /etc/hosts
  - path: "/etc/systemd/resolved.conf"
    permissions: "0644"
    owner: "root"
    content: |
      [Resolve]
      DNS=ad_server_ip
      Domains=sts.test
  - path: "/etc/sssd/conf.d/sssd_debug.conf"
    permissions: "0600"
    owner: "root"
    content: |
      [sssd]
      debug_level = 7
runcmd:
  - [/tmp/post-install.sh]
  - [mv, /etc/krb5.conf, /etc/krb5.conf.orig]
  - [debconf-set-selections, /tmp/krb5-config.debconf]
  - [dpkg-reconfigure, -fnoninteractive, krb5-config]
  - [systemctl, restart, systemd-resolved]
```

Now you can run './build.sh', and wait for the two servers to start up, configure themselves and be ready to log in and test AD joins and authentication. 

Once you've run 'build.sh', it will return the information you need to log into your hosts. 

Log into the client as suggested, and run the following commands:

    kinit Administrator@STS.TEST

This will prompt for a password. Use the password shown at the end of running 'build.sh'

If that returns with success, you can then check your Kerberos ticket with:

    klist

Now you can join your machine to the AD domain, presented by the configured 'sssd-server' instance you created:

    sudo realm join -U Administrator@STS.TEST sts.test --verbose

Once joined to the domain, you can confirm the domain with:

    sudo realm discover STS.TEST


    getent passwd Administrator@STS.TEST
    id Administrator@STS.TEST
    groups Administrator@STS.TEST

Let's configure PAM to create home directories for domain users who log in, automatically:

    sudo pam-auth-update --enable mkhomedir
    sudo systemctl restart sssd

Now when the domain users log in, they'll have a home directory created for them as they log in. You can tune the naming convention/path of th is directory by updating the '/etc/sssd/sssd.conf' file to include the following line:

    override_homedir = /home/%d/%u

This will create a directory that looks like:

    /home/sts.test/Administrator

Now you can log into the domain with this user, with the following:

    sudo login

The username you'll need to use has to include the domain postfix, so in this case, we'll use: 'Administrator@STS.TEST'. Enter the password as before, and you should now be sitting in your new domain home directory.

You can also log in via ssh, using the following construct:

    ssh Administrator@STS.TEST@other-machine.sts.test

To create additional users that can log into the domain, you can use the following:

    sudo samba-tool user create testuser

To allow 'lightdm' to authenticate a non-local user, you need to update the lightdm configuration with a small but of customization: 

In /etc/lightdm/lightdm.conf.d/, create a file called '10-sssd.conf' with the following contents: 

    [Seat:*]
    greeter-hide-users=false
    greeter-show-manual-login=true
    allow-guest=false

After saving that file, restart lightdm to activate that configuration: 

    sudo systemctl restart lightdm



## Related documents

- [Setting up Samba as an Active Directory Domain Controller](https://wiki.samba.org/index.php/Setting_up_Samba_as_an_Active_Directory_Domain_Controller)
