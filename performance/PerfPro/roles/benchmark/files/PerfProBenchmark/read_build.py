#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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

import os
import sys
import yaml
import re

conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)
release_info = str(parse_conf.get('BUILD_INFO'))
build_url = parse_conf.get('BUILD_URL')
docker_info = parse_conf.get('DOCKER_INFO')

'''
Function to get the release info from the Docker image.
It returns the value for the variable(BUILD) which is required by the script.
'''


def get_build_info(variable):
    release_info = os.popen('docker run --rm -it ' +
                            docker_info + ' cat /opt/seagate/cortx/RELEASE.INFO')
    lines = release_info.readlines()
    for line in lines:
        if variable in line:
            strinfo = line.strip()
            strip_strinfo = re.split(': ', strinfo)
            return(strip_strinfo[1])


if release_info == 'RELEASE.INFO':
    version = get_build_info('VERSION')[1:-1]
    ver_strip = re.split('-', version)
    BUILD = ver_strip[1]
    print(BUILD)
elif release_info == 'USER_INPUT':
    BUILD = parse_conf.get('BUILD')
    print(BUILD)
