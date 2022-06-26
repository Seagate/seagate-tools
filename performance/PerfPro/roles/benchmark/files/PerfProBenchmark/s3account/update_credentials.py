#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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
"""This Module will update S3 user credentials in client machine"""

import sys


def main(argv):
    access = sys.argv[1]
    secretkey = sys.argv[2]
    content = "[default]\naws_access_key_id = {}\naws_secret_access_key = {}".format(
        access, secretkey)
    try:
        with open("/root/.aws/credentials", 'w') as f:
            f.write(content)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main(sys.argv)
