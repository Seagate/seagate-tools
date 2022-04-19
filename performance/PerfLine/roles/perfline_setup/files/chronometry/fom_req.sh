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
#


set -e

# Choose one of the patterns
PATTERN="%WRITEV%"   # IO write
#PATTERN="%READV%"    # IO read
#PATTERN="%CAS_PUT%"  # CAS put
#PATTERN="%CAS_GET%"  # CAS get

# SQL limit settings
LIMIT_OFFSET=1000
LIMIT=10

echo "============================================================="
echo "Pattern: $PATTERN, limit offset: $LIMIT_OFFSET, limit: $LIMIT"
echo "============================================================="

for x in $(echo "select fom_sm_id, pid from fom_desc where req_opcode like '$PATTERN' limit $LIMIT_OFFSET,$LIMIT;" | sqlite3 m0play.db); do
    IFS='|' read -r -a args <<< "$x"
    echo "FOM id: ${args[0]}, pid: ${args[1]}"
    python3 fom_req.py -f ${args[0]} -p ${args[1]}
    echo "-------------------------------------------------------------"
done
