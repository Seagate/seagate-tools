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
from os.path import join, isdir
from flask import send_file

from app_global_data import *


@app.route('/report/<string:tid>/dstat_imgs/<string:node_id>/<string:img_type>')
def serve_dstat_imgs(tid, node_id, img_type):
    # Easy safe check
    if ':' in img_type or '/' in img_type or '|' in img_type or ';' in img_type:
        return None

    location = cache.get_location(tid)
    path_to_stats = f'{location}/result_{tid}/stats'
    nodes_stat_dirs = [join(path_to_stats, f) for f in os.listdir(
        path_to_stats) if isdir(join(path_to_stats, f))]

    path_to_img = join(
        nodes_stat_dirs[int(node_id)], 'dstat', img_type + '.png')
    return send_file(path_to_img, mimetype='image')
