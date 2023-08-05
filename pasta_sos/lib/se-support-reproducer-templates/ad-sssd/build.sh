#!/bin/bash
# set for debugging
set -x

if [[ -f $1 ]]; then
  pubkey="$1";
elif [[ -f ~/.ssh/id_rsa.pub ]]; then
  echo "No ssh public key input provided, using default ssh public key location: ~/.ssh/id_rsa.pub"
  pubkey=~/.ssh/id_rsa.pub;
else
  echo "No ssh public key provided, and no default ssh public key found, please provide an ssh public key as an input to this script."; exit 1;
fi

os_series=bionic

# These CANNOT be greater than 15 characters because of netbios limits
server_hostname=ad-server
client_hostname=ad-client

krb5_domain=STS
sssd_realm=STS.TEST

# Could use ${sssd_realm,,} to lowercase the above if same as dns_domain
dns_domain=sts.test

passwd=$(mkpasswd --method=SHA-512 --rounds=4096 ubuntu)
krb5_passwd=$(openssl rand -base64 12)
ssh_pubkey=$(cat "$pubkey")

uvt_opts=('arch=amd64' '--memory 2048' '--cpu 2' '--disk 10')

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
printf '.'
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

echo -e "In a few moments, you can ssh to the client with:\n\n" \
"ssh -i $pubkey ubuntu@\$(uvt-kvm ip $client_hostname)\n" \
"ssh -i $pubkey ubuntu@\$(uvt-kvm ip $server_hostname)\n"
printf "Your password for the Administrator account is: ${krb5_passwd}\n"
