#!/usr/bin/env bash
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.
#

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