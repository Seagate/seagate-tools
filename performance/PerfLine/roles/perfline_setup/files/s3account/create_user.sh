#/bin/bash

set -x




CONST_KEY=`cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'const_key=' | awk -F= '{print $2}'`
echo "$CONST_KEY"
ENCPW=`cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'LoginPW=' | cut -c 13-`
echo $ENCPW
KEY=`s3cipher generate_key --const_key $CONST_KEY`
LDAPPWD=`s3cipher decrypt --data $ENCPW --key $KEY`
s3iamcli CreateAccount -n test${RANDOM:0:3} -e cloud${RANDOM:0:3}@seagate.com --ldapuser sgiamadmin --ldappasswd $LDAPPWD --no-ssl > s3user.txt
cat s3user.txt

