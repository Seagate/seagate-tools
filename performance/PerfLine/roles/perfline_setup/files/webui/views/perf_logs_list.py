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