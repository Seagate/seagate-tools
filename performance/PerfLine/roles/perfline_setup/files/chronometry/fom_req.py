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
#

import sys
from addb2db import *
from typing import List, Dict
from req_utils import *


def get_timelines(fom_id: int, pid: int):
    time_table = []

    fom_desc_d = query2dlist(fom_desc.select().where((fom_desc.fom_sm_id==fom_id)&
                                                     (fom_desc.pid==pid)))
    assert(len(fom_desc_d) == 1)
    fom_state_id = fom_desc_d[0]['fom_state_sm_id']

    fom_req_st_d = query2dlist(fom_req_state.select().where((fom_req_state.id==fom_state_id)&(fom_req_state.pid==pid)))
    times_tag_append(fom_req_st_d, 'op', f"fom-state {fom_state_id}")
    time_table.append(fom_req_st_d)

    fom_req_d = query2dlist(fom_req.select().where((fom_req.id==fom_id)&(fom_req.pid==pid)))
    times_tag_append(fom_req_d, 'op', f"fom-phase {fom_id}")
    time_table.append(fom_req_d)

    stob_ids = query2dlist(fom_to_stio.select().where((fom_to_stio.fom_id==fom_id)&(fom_to_stio.pid==pid)))

    for sid in stob_ids:
        stio_d = query2dlist(stio_req.select().where((stio_req.id==sid['stio_id'])&(stio_req.pid==pid)))
        times_tag_append(stio_d, 'op', f"stob_io {sid['stio_id']}")
        time_table.append(stio_d)

    tx_ids = query2dlist(fom_to_tx.select().where((fom_to_tx.fom_id==fom_id)&(fom_to_tx.pid==pid)))

    for tx in tx_ids:
        tx_d = query2dlist(be_tx.select().where((be_tx.id==tx['tx_id'])&(be_tx.pid==pid)))
        times_tag_append(tx_d, 'op', f"tx {tx['tx_id']}")
        time_table.append(tx_d)

    prepare_time_table(time_table)

    return time_table


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    fom_req.py: Display FOM-related timelines.
    """)
    parser.add_argument("-f", "--fom-id", type=int, required=True,
                        help="FOM id")
    parser.add_argument("-p", "--pid", type=int, required=True,
                        help="Server pid to get FOM phases")
    parser.add_argument("-v", "--verbose", action='count', default=0)
    parser.add_argument("-u", "--time-unit", choices=['ms','us'], default='us',
                        help="Default time unit")
    parser.add_argument("-m", "--maximize", action='store_true',
                        help="Display in maximised window")
    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")

    return parser.parse_args()

if __name__ == '__main__':
    args=parse_args()

    db_init(args.db)
    db_connect()

    print("Getting timelines...")

    time_table = get_timelines(args.fom_id, args.pid)

    db_close()

    print("Plotting timelines...")

    draw_timelines(time_table, None, 0, 0, args.time_unit, False, args.maximize)

# ================================================================================
