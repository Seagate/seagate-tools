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

from flask import send_file

from app_global_data import *


@app.route('/report/<string:tid>/imgs/<string:node_id>/<string:img_type>')
def serve_report_imgs(tid, node_id, img_type):
    imgs_dict = report_resource_map.get(tid)
    print(imgs_dict)
    path_to_img = imgs_dict.get(img_type)[int(node_id)]
    return send_file(path_to_img, mimetype='image/svg+xml' if img_type == 'blktrace' else 'image')
