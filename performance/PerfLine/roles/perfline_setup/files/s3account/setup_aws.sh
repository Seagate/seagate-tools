#/bin/bash

set -x

curl https://raw.githubusercontent.com/Seagate/cortx-s3server/main/ansible/files/certs/stx-s3-clients/s3/ca.crt -o /etc/ssl/ca.crt
AWSKEYID=`cat s3user.txt |cut -d ',' -f 4 |cut -d ' ' -f 4`
AWSKEY=`cat s3user.txt |cut -d ',' -f 5 |cut -d ' ' -f 4`
pip3 install -i https://pypi.org/simple awscli
pip3 install -i https://pypi.org/simple awscli-plugin-endpoint
aws configure set aws_access_key_id $AWSKEYID
aws configure set aws_secret_access_key $AWSKEY
aws configure set plugins.endpoint awscli_plugin_endpoint
aws configure set s3.endpoint_url http://s3.seagate.com
aws configure set s3api.endpoint_url http://s3.seagate.com
aws configure set ca_bundle '/etc/ssl/ca.crt'
cat ~/.aws/config
cat ~/.aws/credentials
aws s3 mb s3://test${RANDOM:0:3}
aws s3 ls

