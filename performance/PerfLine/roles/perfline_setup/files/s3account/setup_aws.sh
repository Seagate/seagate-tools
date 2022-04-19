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

