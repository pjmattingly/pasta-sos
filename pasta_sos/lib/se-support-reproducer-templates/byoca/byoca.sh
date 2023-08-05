#!/bin/bash

if [ -z "$CA_PASS" ]; then
	read -sp "Enter password: " pass
fi

# Create Root Certificate Authority
mkdir ca
cp openssl-ca.cnf ca/openssl.cnf
cd ca
mkdir certs crl newcerts private
chmod 700 private
touch index.txt
echo 1000 > serial
openssl genrsa -aes256 -passout pass:"$pass" -out private/ca.key.pem 4096
chmod 400 private/ca.key.pem
openssl req -config openssl.cnf \
      -passin pass:"$pass" \
      -key private/ca.key.pem \
      -new -x509 -days 7300 -sha256 -extensions v3_ca \
      -out certs/ca.cert.pem
chmod 444 certs/ca.cert.pem

# Create Intermediate CA
mkdir intermediate
cp ../openssl-inter.cnf intermediate/openssl.cnf
cd intermediate
mkdir certs crl csr newcerts private
chmod 700 private
touch index.txt
echo 1000 > serial
echo 1000 > crlnumber
cd ..
openssl genrsa -aes256 \
      -passout pass:"$pass" \
      -out intermediate/private/intermediate.key.pem 4096
chmod 400 intermediate/private/intermediate.key.pem
openssl req -config intermediate/openssl.cnf -new -sha256 \
      -passin pass:"$pass" \
      -key intermediate/private/intermediate.key.pem \
      -out intermediate/csr/intermediate.csr.pem
openssl ca -config openssl.cnf -extensions v3_intermediate_ca \
      -subj '/C=GB/ST=England/L=London/O=Alice Ltd/CN=Intermediate CA/emailAddress=intermediateCA@example.com' \
      -passin pass:"$pass" \
      -batch \
      -days 3650 -notext -md sha256 \
      -in intermediate/csr/intermediate.csr.pem \
      -out intermediate/certs/intermediate.cert.pem
chmod 444 intermediate/certs/intermediate.cert.pem
cat intermediate/certs/intermediate.cert.pem \
      certs/ca.cert.pem > intermediate/certs/ca-chain.cert.pem
chmod 444 intermediate/certs/ca-chain.cert.pem

# Sign Example Certificates
for name in bob carol dan oscar; do
	openssl genrsa -aes256 \
	    -passout pass:"$pass" \
      	-out intermediate/private/"$name".example.com.key.pem 2048
	openssl req -config intermediate/openssl.cnf \
	      -passin pass:"$pass" \
	      -key intermediate/private/"$name".example.com.key.pem \
	      -new -sha256 -out intermediate/csr/"$name".example.com.csr.pem
	openssl ca -config intermediate/openssl.cnf \
	      -subj "/C=GB/ST=England/L=London/O=Alice Ltd/CN=${name}.example.com/emailAddress=${name}@example.com" \
	      -passin pass:"$pass" \
	      -batch \
	      -extensions server_cert -days 375 -notext -md sha256 \
	      -in intermediate/csr/"$name".example.com.csr.pem \
	      -out intermediate/certs/"$name".example.com.cert.pem
	chmod 444 intermediate/certs/"$name".example.com.cert.pem
done

# Generate CRL
for name in carol oscar; do
	openssl ca -config intermediate/openssl.cnf \
	      -passin pass:"$pass" \
	      -revoke intermediate/certs/"$name".example.com.cert.pem
done
openssl ca -config intermediate/openssl.cnf \
      -passin pass:"$pass" \
      -gencrl -out intermediate/crl/intermediate.crl.pem

# Generate OCSP
openssl genrsa -aes256 \
      -passout pass:"$pass" \
      -out intermediate/private/ocsp.key.pem 4096
openssl req -config intermediate/openssl.cnf -new -sha256 \
      -passin pass:"$pass" \
      -key intermediate/private/ocsp.key.pem \
      -out intermediate/csr/ocsp.csr.pem
openssl ca -config intermediate/openssl.cnf \
      -subj "/C=GB/ST=England/L=London/O=Alice Ltd/CN=OCSP Endpoint/emailAddress=ocsp@example.com" \
      -passin pass:"$pass" \
      -batch \
      -extensions ocsp -days 375 -notext -md sha256 \
      -in intermediate/csr/ocsp.csr.pem \
      -out intermediate/certs/ocsp.cert.pem

# Test Certificate Verification
echo -e "\n\nTesting OCSP verification...\n"
set -x
openssl ocsp -port 2560 -text \
      -passin pass:"$pass" \
      -index intermediate/index.txt \
      -CA intermediate/certs/ca-chain.cert.pem \
      -rkey intermediate/private/ocsp.key.pem \
      -rsigner intermediate/certs/ocsp.cert.pem \
      -nrequest 1000 &
sleep 1
openssl ocsp -CAfile intermediate/certs/ca-chain.cert.pem \
      -issuer intermediate/certs/intermediate.cert.pem \
      -cert intermediate/certs/oscar.example.com.cert.pem \
      -url http://localhost:2560
set +x
killall openssl

# Print Results
echo -e "\n\nComplete! You will find all files for the root CA, intermediate CA, user/server certificates, and CRLs in the \"ca\" folder.\n\nRoot CA Name: Alice Ltd\nCertificates:\nbob.example.com - OK\ncarol.example.com - REVOKED\ndan.example.com - OK\noscar.example.com - REVOKED\nCRL URI: http://localhost/intermediate.crl.pem\n\nScroll up to see the commands and test results for OCSP verification."
