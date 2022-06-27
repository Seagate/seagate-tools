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

from flask import make_response

from app_global_data import app, cache, all_artif_dirs

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
             print(f"Failed task deletion: {error}")
    cache.update(all_artif_dirs, force = True)
    response = make_response(f'{result}')
    return response

