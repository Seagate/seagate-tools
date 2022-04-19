#!/usr/bin/env python3
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

import os
import sys
import yaml
from os.path import isdir, join
from flask import request, make_response

from app_global_data import *
sys.path.insert(0, VALIDATOR)
import validator as vr


@app.route('/api/task/saveData/<string:task>', methods = ["POST"])
def saveFile(task: str):
    config: str = request.form['config']
    CUSTOM_DIR = os.path.join(WORKLOAD_DIR,'custom_workload')
    config1 = yaml.safe_load(config)
    prio = config1['common']['priority']

    files = os.listdir(f'{WORKLOAD_DIR}')
    if task+'.yaml' in files:
       result = { 'Failed': 'Sorry! you can\'t edit \"example.yaml\". Please use different filename' }

    else:
       if not isdir(CUSTOM_DIR):
            os.mkdir(CUSTOM_DIR)
       filename: str = join(CUSTOM_DIR, task+'.yaml')
       errors = vr.validate_config(config1)
       if all([v for e in errors for v in e.values()]):
           result = errors
       elif HIGHEST_WEBUI_PRIO < prio or prio < LOWEST_PRIO:
           result = { 'PRIORITY': f'Too high priority are not allowed. Please use between {LOWEST_PRIO} to {HIGHEST_WEBUI_PRIO}'}
       else:
           with open(filename, 'w') as output:
                output.write(config)
           result = { 'Success': 'Successfully added new workload' }
    response = make_response(f'{result}')
    return response
