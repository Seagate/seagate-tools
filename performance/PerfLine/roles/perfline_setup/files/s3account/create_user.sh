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




CONST_KEY=$(cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'const_key=' | awk -F= '{print $2}')
echo "$CONST_KEY"
ENCPW=$(cat /opt/seagate/cortx/auth/resources/authserver.properties | grep 'LoginPW=' | cut -c 13-)
echo "$ENCPW"
KEY=$(s3cipher generate_key --const_key "$CONST_KEY")
LDAPPWD=$(s3cipher decrypt --data "$ENCPW" --key "$KEY")
s3iamcli CreateAccount -n test${RANDOM:0:3} -e cloud${RANDOM:0:3}@seagate.com --ldapuser sgiamadmin --ldappasswd "$LDAPPWD" --no-ssl > s3user.txt
cat s3user.txt

