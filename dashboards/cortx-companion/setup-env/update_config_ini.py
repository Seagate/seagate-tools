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
"""Automates updation of config.ini file."""

import configparser
import os
import sys

cur_dir = os.getcwd()
req_path = "/seagate-tools/dashboards/cortx-companion/config.ini"
filepath = cur_dir+req_path

parser = configparser.ConfigParser()
parser.read(filepath)

t = open(filepath, 'w')

parser.set('PERF_DB', 'db_username', sys.argv[3])
parser.set('PERF_DB', 'db_password', sys.argv[4])

parser.set('REST', 'db_username', sys.argv[1])
parser.set('REST', 'db_password', sys.argv[2])

parser.set('MONGODB_URI', 'db_username', sys.argv[1])
parser.set('MONGODB_URI', 'db_password', sys.argv[2])

parser.set('JIRA', 'jira_username', sys.argv[5])
parser.set('JIRA', 'jira_password', sys.argv[6])
parser.write(t)

t.close()
print("*************updated credentials of config.ini****************")
