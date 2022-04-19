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

attr={ "name": "s3_req" }
def query(from_, to_):
    q=f"""
    SELECT (SELECT MIN(to_.time)
            FROM s3_request_state AS to_
            WHERE to_.id = frm.id
              AND to_.pid = frm.pid
              AND to_.time > frm.time
              AND to_.state = "{to_}") - frm.time AS time,
           "{from_}",
           "{to_}",
           frm.id
    FROM s3_request_state AS frm
    JOIN (SELECT flt.pid, flt.id
          FROM s3_request_state AS flt
          WHERE flt.state = "{to_}") filter_state
    ON filter_state.id = frm.id AND filter_state.pid = frm.pid
    WHERE frm.state="{from_}";
    """
    return q

if __name__ == '__main__':
    import sys
    sys.exit(1)
