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
import json
import uuid
import gzip
from flask import request, make_response

from app_global_data import *


logcookies = {}


@app.route('/api/log/<string:morelines>')
def getlog(morelines: str):
    cookie = request.cookies.get('logcookie')
    logf = None
    uid = None

    # coookie found and active, log is opened
    if cookie and logcookies.get(cookie):
        logf = logcookies[cookie]
    # no coookie found: open log, seek to its end
    else:
        uid = str(uuid.uuid1())
        logf = open(LOGFILE, "r")
        logf.seek(0, os.SEEK_END)
        logcookies.update({uid: logf})

    # if morelines == "true":  # [sigh]
    #     logf.seek(0, os.SEEK_END)
    #     logf.seek(logf.tell() - 2048, os.SEEK_SET)

    data = {
        "tqlog": "".join(list(logf.readlines()))
    }
    content = gzip.compress(json.dumps(data).encode('utf8'), 5)
    response = make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    if uid:
        response.set_cookie('logcookie', uid)
    return response
