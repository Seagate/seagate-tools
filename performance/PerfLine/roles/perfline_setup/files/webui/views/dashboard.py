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
import sys
import gzip
from flask import send_file, request, make_response

from app_global_data import *


@app.route('/dashboard/logo')
def serve_logo_imgs():
    return send_file("img/logo.png", mimetype='image')

@app.route('/dashboard/plot')
def serve_plots():
    build = request.args.get('build')
    size = request.args.get('size')
    sessions = request.args.get('sessions')

    f = 'img/not_found.png'
    name = os.path.join(build, "img", '_'.join([size, sessions]) + ".png")
    for d in night_daemon_dirs:
        ff = os.path.join(d, name)
        if os.path.isfile(ff):
            f = ff
            break

    return send_file(f, mimetype='image')


@app.route('/dashboard/table')
def server_table():
    build = request.args.get('build')
    size = request.args.get('size')
    sessions = request.args.get('sessions')

    f = ''
    name = os.path.join(build, "data", '_'.join([size, sessions]) + ".json")
    for d in night_daemon_dirs:
        ff = os.path.join(d, name)
        if os.path.isfile(ff):
            f = ff
            break

    if not f:
        return make_response("data not found", 404)
    else:
        with open(f, 'r') as fd:
            content = gzip.compress(fd.read().encode('utf8'), 5)
            response = make_response(content)
            response.headers['Content-length'] = len(content)
            response.headers['Content-Encoding'] = 'gzip'
            return response
