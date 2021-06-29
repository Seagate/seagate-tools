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

from flask import make_response

from app_global_data import *

from core.utils import tq_task_common_get

from shutil import rmtree

@app.route('/api/results/delete/<string:taskList>')
def deleteTask(taskList: str):
    result = {}
    for taskid in list(taskList.split(",")):
         location = cache.get_location(taskid)
         result_dir = f'{location}/result_{taskid}/'
         try:
             rmtree(result_dir)
             result[result_dir] = "deleted successfully"
         except OSError as error:
             result[result_dir] = "File path not found"
    cache.update(config.artifacts_dirs, force = True)
    response = make_response(f'{result}')
    return response

