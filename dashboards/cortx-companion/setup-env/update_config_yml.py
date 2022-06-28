#!/usr/bin/env python3
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
"""Automates updation of config.yml file."""

import yaml
import os
import sys

cur_dir = os.getcwd()
req_path = "/seagate-tools/dashboards/cortx-companion/Performance/configs.yml"
filepath = cur_dir+req_path


def read_file():
    with open(filepath, 'r') as f:
        y = yaml.safe_load(f)
        return y


data = read_file()

with open(filepath, 'w') as f:
    data['PerfDB']['auth']['full_access_user'] = sys.argv[1]
    data['PerfDB']['auth']['full_access_password'] = sys.argv[2]
    yaml.dump(data, f,  default_flow_style=False, sort_keys=False)

print("*************updated credentials of configs.yml***************")
