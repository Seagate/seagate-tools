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

from flask import make_response, request

from app_global_data import *
from core import pl_api
import yaml

@app.route('/addtask', methods = ["POST"])
def addtask():
    config: str = request.form['config']
    config1 = yaml.safe_load(config)
    prio = config1['common']['priority']
    if HIGHEST_PRIO < prio or prio < LOWEST_PRIO:
        result = { 'PRIORITY': 'Too high priority are not allowed. Please use between 1 to 3' }
    else:
        result = pl_api.add_task(config)
    response = make_response(f'{result}')
    return response
