#/bin/bash

set -x

wget http://cortx-storage.colo.seagate.com/releases/cortx/github/stable/centos-7.8.2003/238/dev/cortx-s3iamcli-2.0.0-68_gitc482a593.noarch.rpm
yum install -y cortx-s3iamcli-2.0.0-68_gitc482a593.noarch.rpm


CONST_KEY=`cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'const_key=' | awk -F= '{print $2}'`
echo $CONST_KEY
ENCPW=`cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'LoginPW=' | cut -c 13-`
echo $ENCPW
KEY=`s3cipher generate_key --const_key $CONST_KEY`
LDAPPWD=`s3cipher decrypt --data $ENCPW --key $KEY`
s3iamcli CreateAccount -n test${RANDOM:0:3} -e cloud${RANDOM:0:3}@seagate.com --ldapuser sgiamadmin --ldappasswd $LDAPPWD --no-ssl > s3user.txt
cat s3user.txt

