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
set -x

function main()
{
    local docker_image_tag="$1"

    if [[ -z "$docker_image_tag" ]]; then
        echo 'missed docker image tag'
        return 1
    fi

    local docker_image_id="$(docker images | grep $docker_image_tag | awk '{print $3}')"

    if [[ -n "$docker_image_id" ]]; then
        docker rmi $docker_image_id || true
    fi
}

main $@
exit $?