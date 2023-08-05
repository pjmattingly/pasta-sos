## Landscape On Prem (cloud-init)

Using the lds.yaml with uvtool (uvt-kvm) should deploy a Landscape On-Prem server (quickstart install) with all the necessary configurations for the client to register itself to the server. 

## The Fiddly Bits

The first Landscape Admin does have to be manually created in the webUI. Further instructions are given in the landscape-phase2.sh script. First run this to initiate the deploy using uvt-kvm.

```
uvt-kvm create landscape-lab release=bionic arch=amd64 --memory 4096 --cpu 4 --disk 20 --host-passthrough --user-data lds.yaml
```

Once the VM is created and running, SSH in with the following command (user: ubuntu; pass: ubuntu)

```
ssh ubuntu@$(uvt-kvm ip landscape-lab)
```

After you are loged in tail the /var/log/cloud-init-output.log to monitor progress of the deployment

```
sudo tail -f /var/log/cloud-init-output.log
```

At the end of the output there should be instructions to run landscape-phase2.sh. This can be run either as root or the ubuntu user.

```
landscape-phase2.sh
```

Follow the instructions given to create the first Landscape Admin user, accept the registration of the machine to itself, and configure landscape-api credentials. 

You should now have a functional Landscape On-Prem server and client machine with API all-in-one to use for testing or reproducing issues as necessary.
