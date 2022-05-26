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
from os.path import join, isdir
from flask import send_file

from app_global_data import app, cache


@app.route('/report/<string:tid>/dstat_imgs/<string:node_id>/<string:img_type>')
def serve_dstat_imgs(tid, node_id, img_type):
    # Easy safe check
    if ':' in img_type or '/' in img_type or '|' in img_type or ';' in img_type:
        return None

    location = cache.get_location(tid)
    path_to_stats = f'{location}/result_{tid}/stats'
    nodes_stat_dirs = [join(path_to_stats, f) for f in os.listdir(
        path_to_stats) if isdir(join(path_to_stats, f)) and not "addb" in f]

    path_to_img = join(
        nodes_stat_dirs[int(node_id)], 'dstat', img_type + '.png')
    return send_file(path_to_img, mimetype='image')
