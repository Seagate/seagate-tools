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

set -e

MOTR_CONF_FILE="/etc/sysconfig/motr"
DEFAULT_MOTR_TRACE_LOCATION="/var/motr"

function main()
{
    local trace_location=$(grep '^\s*MOTR_M0D_TRACE_DIR' $MOTR_CONF_FILE \
                            | awk -F '=' '{print $2}' \
                            | sed 's/^ *//' | sed 's/ *$//')

    if [[ -n "$trace_location" ]]; then
        echo "$trace_location"
    else
        echo "$DEFAULT_MOTR_TRACE_LOCATION"
    fi
}

main $@
exit $?