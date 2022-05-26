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
import gzip
from flask import send_file, request, make_response

from app_global_data import app, night_daemon_dirs


@app.route('/dashboard/logo')
def serve_logo_imgs():
    return send_file("img/logo.png", mimetype='image')

@app.route('/dashboard/plot')
def serve_plots():
    args = request.args
    if 'build' not in args or 'size' not in args or 'sessions' not in args:
        return make_response("required parameter not found", 400)

    build = args.get('build')
    size = args.get('size')
    sessions = args.get('sessions')

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
    args = request.args
    if 'build' not in args or 'size' not in args or 'sessions' not in args:
        return make_response("required parameter not found", 400)

    build = args.get('build')
    size = args.get('size')
    sessions = args.get('sessions')

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
