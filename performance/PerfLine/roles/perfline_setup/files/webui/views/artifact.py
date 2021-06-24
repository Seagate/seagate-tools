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
from flask import send_from_directory, make_response

from app_global_data import *


@app.route('/artifacts/<uuid:task_id>/<path:subpath>')
def get_artifact(task_id, subpath):
    task_id = str(task_id)

    if cache.has(task_id):
        location = cache.get_location(task_id)
        path = 'result_{0}/{1}'.format(task_id, subpath)
        return send_from_directory(location + '/', path)
    else:
        return make_response('not found', 404)
