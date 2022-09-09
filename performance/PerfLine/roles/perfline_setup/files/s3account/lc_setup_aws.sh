#!/usr/bin/env bash
#
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#
# -*- coding: utf-8 -*-

set -x

if [ $# -lt 1  ]
then
  echo; echo "Usage: $0 <rgw|s3srv>"
  echo; echo "eg:"
  echo; echo "    # $0 rgw "
  echo; echo "or"
  echo; echo "    # $0 s3srv"
  exit
fi


AWSKEYID=$(cat s3user.txt |cut -d ',' -f 4 |cut -d ' ' -f 4)
AWSKEY=$(cat s3user.txt |cut -d ',' -f 5 |cut -d ' ' -f 4)
aws configure set aws_access_key_id "$AWSKEYID"
aws configure set plugins.endpoint awscli_plugin_endpoint
aws configure set s3.endpoint_url http://s3.seagate.com
aws configure set s3api.endpoint_url http://s3.seagate.com
aws configure set ca_bundle '/etc/ssl/ca.crt'

if [ "$1" == "rgw" ]
then 
    SKEY=$(sudo kubectl get secrets cortx-secret  --template={{.data.s3_auth_admin_secret}}  | base64 -d)
    aws configure set aws_secret_access_key "$SKEY"
else
    aws configure set aws_secret_access_key "$AWSKEY"
fi

cat ~/.aws/config
cat ~/.aws/credentials
