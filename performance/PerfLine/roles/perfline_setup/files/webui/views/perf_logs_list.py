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
from flask import render_template, make_response

from app_global_data import *


@app.route('/log/<uuid:task_id>')
def perflinelog_list_page(task_id):
    task_id = str(task_id)
    files = list()

    location = cache.get_location(task_id)
    
    logs_dir = '{0}/result_{1}/log'.format(location, task_id)
    if not os.path.isdir(logs_dir):
        return make_response('logs not found', 404)
        
    for item in os.walk(logs_dir):
        for file_name in item[2]:
            dir_name = item[0].replace(
                '{0}/result_{1}'.format(location, task_id), '', 1)
            files.append('{0}/{1}'.format(dir_name, file_name))
    context = dict()
    context['task_id'] = task_id
    context['files'] = files
    return render_template("perf_log.html", **context)