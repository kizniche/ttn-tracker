#!/bin/bash

printf "\n#### Checking for SSL certificates in /var/ttn_tracker/ssl_certs/\n"
if [ ! -e /var/ttn_tracker/ssl_certs/server.crt ]; then
    printf "\n#### Generating SSL certificates in /var/ttn_tracker/ssl_certs/\n"
    cd /var/ttn_tracker/ssl_certs/
    rm -f ./*.pem ./*.csr ./*.crt ./*.key
    openssl genrsa \
        -out /var/ttn_tracker/ssl_certs/server.pass.key 4096
    openssl rsa \
        -in /var/ttn_tracker/ssl_certs/server.pass.key \
        -out /var/ttn_tracker/ssl_certs/server.key
    rm -f /var/ttn_tracker/ssl_certs/server.pass.key
    openssl req -new \
        -key /var/ttn_tracker/ssl_certs/server.key \
        -out /var/ttn_tracker/ssl_certs/server.csr \
        -subj "/O=mycodo/OU=mycodo/CN=mycodo"
    openssl x509 -req \
        -days 3653 \
        -in /var/ttn_tracker/ssl_certs/server.csr \
        -signkey /var/ttn_tracker/ssl_certs/server.key \
        -out /var/ttn_tracker/ssl_certs/server.crt
else
    printf "\n#### SSL certificates exist in /var/ttn_tracker/ssl_certs/, skipping generation\n"
fi