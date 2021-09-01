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
       elif HIGHEST_PRIO < prio or prio < LOWEST_PRIO:
           result = { 'PRIORITY': 'Too high priority are not allowed. Please use between 1 to 3'}
       else:
           with open(filename, 'w') as output:
                output.write(config)
           result = { 'Success': 'Successfully added new workload' }
    response = make_response(f'{result}')
    return response
