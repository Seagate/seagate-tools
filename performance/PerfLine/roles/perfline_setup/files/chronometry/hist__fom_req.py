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

attr={ "name": "fom_req" }

def query(from_, to_):
    q=f"""
    SELECT (fr.time-fom_req.time) as time, fom_req.state, fr.state, fr.id FROM fom_desc
    JOIN fom_req on fom_desc.fom_sm_id=fom_req.id and fom_desc.pid=fom_req.pid
    JOIN fom_req fr ON fr.id=fom_req.id and fr.pid=fom_req.pid

    WHERE fom_desc.req_opcode LIKE '%WRITE%'
    AND fom_req.state="{from_}"
    AND fr.state="{to_}";
    """
    return q

if __name__ == '__main__':
    import sys
    sys.exit(1)
