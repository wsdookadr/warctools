#!/bin/bash
rm -rf .pki/
mkdir -p ~/.pki/nssdb/
certfile=~/.mitmproxy/mitmproxy-ca.pem
certutil --empty-password -N -d sql:.pki/nssdb/

for certDB in $(find ~/.pki -name "cert9.db")
do
    certdir=$(dirname ${certDB});
    certutil -A -n "${certname}" -t "TCu,Cu,Tu" -i ${certfile} -d sql:${certdir}
done
certutil -L -d sql:.pki/nssdb/

