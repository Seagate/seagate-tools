#!/bin/sh
#
# Seagate-tools: PerfPro
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

set -e
#read -p "Enter the label for S3 setup:" s3_setup_label
#read -p "S3 endpoint url:" s3_url_endpoint
#read -p "Access Key:" s3_access_key
#read -p "Secret Key:" s3_secret_key

#s3_setup_label="$s3_setup_label.properties"
s3_setup_label=s3setup.properties
s3_url_endpoint="$1"
s3_access_key=$(grep -A 3 default /root/.aws/credentials | grep aws_access_key_id | cut -d " " -f3)
s3_secret_key=$(grep -A 3 default /root/.aws/credentials | grep secret_access_key | cut -d " " -f3)
echo "s3_endpoint:$s3_url_endpoint" > "$s3_setup_label"
echo "access_key:$s3_access_key" >> "$s3_setup_label"
echo "secret_key:$s3_secret_key" >> "$s3_setup_label"
printf "\nCreated S3 setup properties file $s3_setup_label\n\n"
