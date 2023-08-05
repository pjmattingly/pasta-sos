## MAAS KVM with LXD (cloud-init)

Using the `automaas_XXX.yaml` files here with uvtool (uvt-kvm) should deploy a MAAS server either from snaps or PPA, either with PostgreSQL in the snaps or external, and with LXD setup as a VM manager to compose, commission, and deploy VMs within the MAAS host. 

## Requirements

You must install [uvtool](https://ubuntu.com/server/docs/virtualization-uvt), and sync the desired images from simplestreams to your machine. These images will be used by uvt-kvm to deploy the new MAAS VM.

```
# Install uvtool
sudo apt -y install uvtool

# Sync simplestreams images
uvt-simplestreams-libvirt --verbose sync arch=amd64

# To sync only a single release
uvt-simplestreams-libvirt --verbose sync arch=amd64 release=bionic
uvt-simplestreams-libvirt --verbose sync arch=amd64 release=focal
uvt-simplestreams-libvirt --verbose sync arch=amd64 release=groovy
```

## The Fiddly Bits

Before running the deployment commads below, you must add your Launchpad username to the yaml file you want to use. There is a line where this is set in a variable. The value of that is set to **CHANGEME** in the script so it is easy to locate. Change that to your LP ID, and save the file. Once the **CHANGEME** line has been updated, run any of the following initiate the deploy using uvt-kvm.

```
# Install an all snap version of MAAS on Focal
uvt-kvm create automaas_snap release=focal label=release arch=amd64 --memory 4096 --cpu 4 --disk 100 --host-passthrough --user-data automaas_snap.yaml

# Install the snap version of MAAS with external Postgres on Focal
uvt-kvm create automaas_postgres release=focal arch=amd64 --memory 16384 --cpu 4 --disk 100 --host-passthrough --user-data automaas_postgres.yaml

# Install the PPA version of MAAS on Focal
uvt-kvm create automaas_ppa release=focal label=release arch=amd64 --memory 16384 --cpu 4 --disk 100 --host-passthrough --user-data automaas_ppa.yaml
```

**Note:** If you want to deploy a PPA install of MAAS 2.9, you will have to select a Focal or newer release for the underlying OS of the VM. 

Once the VM is created and running (it does not have to be fully deployed), SSH into the VM with the following command. `uvt-kvm` will look up the IP of the VM for you. Credentials for the VM are: user: ubuntu; pass: ubuntu

```
ssh ubuntu@$(uvt-kvm ip automaas_XXX)
```

After you are logged in, tail the `/var/log/cloud-init-output.log` to monitor progress of the deployment

```
sudo tail -f /var/log/cloud-init-output.log
```

At the end of the output there should be instructions to run `maas-phase2.sh`. This can be run either as root or the ubuntu user.

```
maas-phase2.sh
```

The script will first create the MAAS admin user, and also setup the API key file. Then follow the instructions given to log into the MAAS interface and configure the LXD KVM (formerly named Pods). Then let the script continue, it will then complete a number of further configurations to get you started.

* The LXD KVM will be configured for overcommit (10x). 
* A reserved dynamic range will be setup on the LXD subnet. 
* DHCP will be enabled for the LXD subnet. 
* Your first LXD VM will be composed and commissioned by MAAS.

**LXD KVM Creation:** This is done manually in the web UI for MAAS, because when done through the UI, the certificate on the LXD listening service will be automatically added as a trusted certificate to MAAS. If the LXD KVM is created in the command line, the adding and trusting of the certificate is not done, and the command fails, saying that it does not trust the certificate on the listening LXD service, so it will not connect.

**Commissioning:** When commissioning MAAS 2.8 will use Bionic by default, but MAAS 2.9 will use Focal by default. Bionic will successfully commission a machine with only 1G of memory, but commissioning with Focal requires 2G succeed. The `maas-phase2.sh` script by default creates the first VM with 1 CPU and 2G memory, so that if you are using MAAS 2.9 this will hopefully succeed without any manual intervention necessary.

You should now have a functional MAAS (Region+Rack) server that is also a KVM host using LXD as the VM manager to use for testing or reproducing issues as necessary.

**Note:** There is also a second script setup in the MAAS VM for just logging into MAAS using the previously created API key file

```
maas-login.sh
```
## Mirroring MAAS Images

Included here is a YAML template that will allow you to automatically create and sync your MAAS images, so you don't have to go back upstream each time you need to rebuild your MAAS, to sync images. To use this, simply run the following: 

```
uvt-kvm create maas-images-mirror release=focal arch=amd64 --memory 4096 --cpu 2 --disk 40 --host-passthrough --user-data maas-images-mirror.yaml
```
This will create a separate KVM machine and drop a systemd unit in place that runs a local script (`sync-maas-images.sh`) on a timer (See: [systemd timers](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)), and syncs the most-recent, LTS and later Ubuntu and CentOS images into the machine. 

This template also exposes that mirror over HTTP, via a local lighttpd instance, which you can reach by pointing your MAAS image repository to the IP of this container (obtained with `uvt-kvm ip maas-images-mirror`), as: http://192.168.8.123/maas/images/ephemeral-v3/daily/ 

Note: you won't be able to openly "browse" this URI, unless you add `dir-listing.activate        = "enable"` to `/etc/lighttpd/lighttpd.conf` on the image and restart lighttpd. You won't need to do that for MAAS to use this mirror, but for debugging you may want to enable this. 

This sync is configured to run every 6 hours, but you can change that to whatever interval you wish by editing the timer.