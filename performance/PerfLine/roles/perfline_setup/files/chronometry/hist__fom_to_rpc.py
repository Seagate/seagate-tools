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

attr={ "name": "fom_to_rpc" }

def query(from_, to_):
    q=f"""
    SELECT (rpc_req.time-fom_req.time), fom_req.state, rpc_req.state
    FROM fom_desc
    JOIN fom_req on fom_req.id=fom_sm_id
    JOIN rpc_req on rpc_req.id=rpc_sm_id
    WHERE fom_desc.req_opcode LIKE "%M0_IOSERVICE_%"
    AND rpc_req.pid=fom_req.pid
    AND rpc_req.state="{to_}" AND fom_req.state="{from_}";
    """
    return q

if __name__ == '__main__':
    import sys
    sys.exit(1)
