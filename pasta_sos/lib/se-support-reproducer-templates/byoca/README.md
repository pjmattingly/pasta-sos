# :closed_lock_with_key: Bring Your Own Certificate Authority (BYOCA)
This project is a scriptification of [Jamie Nguyen's tutorial](https://jamielinux.com/docs/openssl-certificate-authority/) for creating a Certificate Authority with `openssl`. With one command, you will create a root CA, intermediate CA, several test server certificates, and a Certificate Revocation List (CRL) file. The script also provides commands for testing Online Certificate Status Protocol (OCSP) verification.

# :arrow_forward: Quickstart
The only input necessary is the password that will be used for all certificates. This value can be set ahead of time as an environment variable `CA_PASS`. If it is not set, the script will prompt for a password.

# :cop: Certificate Verification
As mentioned, the script will run a local OCSP server, verify a revoked certificate against it, and display the commands necessary to do so. The endpoint certificates are also encoded with a CRL distribution point that links to [http://localhost/intermediate.crl.pem](http://localhost/intermediate.crl.pem), but `byoca` will not automatically run a web server to host the file, which is found in `./ca/intermediate/crls/intermediate.crl.pem`. This file can be hosted locally using any web server software or can be provided to applications as is.
