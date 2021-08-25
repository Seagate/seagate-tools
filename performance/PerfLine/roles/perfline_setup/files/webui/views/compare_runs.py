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
from flask import make_response, request, render_template

from app_global_data import *


@app.route('/compare_runs')
def compare_runs():
    task_ids = request.args.getlist('task_id')

    if len(task_ids) == 0:
        return make_response("task_id parameter not found", 400)

    context = dict()
    context['task_ids'] = task_ids

    return render_template("compare_runs.html", **context)
