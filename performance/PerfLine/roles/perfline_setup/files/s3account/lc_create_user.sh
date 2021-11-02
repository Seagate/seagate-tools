#/bin/bash

set -x

s3iamcli CreateAccount -n test${RANDOM:0:3} -e cloud${RANDOM:0:3}@seagate.com --ldapuser sgiamadmin --ldappasswd ldapadmin --no-ssl > s3user.txt
cat s3user.txt
