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


@app.route('/api/task/backup_tasks/<string:task_id_list>')
def backup_task(task_id_list):

    if len(backup_artifacts_dirs) == 0:
        err_resp = {"status": "failed",
                    "error_message": "directory for backups was not specified"}

        response = make_response(f'{err_resp}')
        return response


    backup_dir = backup_artifacts_dirs[0]

    result = dict()
    result['status'] = 'success'
    result['detailed_status'] = []

    for task_id in task_id_list.split(","):

        if not task_id:
            continue


        task_status = dict()
        result['detailed_status'].append(task_status)
        task_status['task_id'] = task_id

        if not cache.has(task_id):
            task_status['status'] = 'failed'
            task_status['error_message'] = f'task does not exist'
            result['status'] = 'failed'
        else:

            task_location = cache.get_location(task_id)


            origin_location = f'{task_location}/result_{task_id}'
            tmp_location = f'{task_location}/moving_{task_id}'
            new_location = f'{backup_dir}/result_{task_id}'

            os.rename(origin_location, tmp_location)

            async_worker.move_dir_async(origin_location, tmp_location, new_location)
            task_status['status'] = 'success'

    cache.update(all_artif_dirs, force = True)
    response = make_response(f'{result}')
    return response
