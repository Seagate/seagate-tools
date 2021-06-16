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
import json
import uuid
import gzip
from flask import request, make_response

from app_global_data import *
import config


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
        logf = open(config.logfile, "r")
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