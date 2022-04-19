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

attr={ "name": "ioo_req" }
def query(from_, to_):
    q=f"""
    SELECT (fr.time-ioo_req.time) as time, ioo_req.state, fr.state, fr.id FROM ioo_req
    JOIN ioo_req fr ON fr.id=ioo_req.id AND fr.pid=ioo_req.pid
    WHERE ioo_req.state="{from_}"
    AND fr.state="{to_}";
    """
    return q

if __name__ == '__main__':
    import sys
    sys.exit(1)
