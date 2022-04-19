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

from addb2db import *
from req_utils import query2dlist, prepare_time_table, draw_timelines, times_tag_append
import sys

time_table = []
visited = set()

def process_req(pid, rid, type_id, level, depth):
    # Fetch children
    req = relation.select().where((relation.pid1 == pid) & (relation.mid1 == rid))
    subreqs = [r for r in req.dicts()]

    # Skip odd RPC connections
    if 'sxid_to_rpc' in type_id and not subreqs:
        return

    # Ignore tx group states
    if type_id == 'tx_to_gr':
        return

    # Fetch timeline
    requests_d = query2dlist(request.select().where((request.id==rid) & (request.pid==pid)))
    if requests_d:
        op = requests_d[0]['type_id']
        times_tag_append(requests_d, 'op', f"{pid}/{rid}/{op}")
        time_table.append(requests_d)

    # Check depth
    if level >= depth:
        return

    # Traverse children
    for subreq in subreqs:
        hsh = f"{subreq['pid2']}_{subreq['mid2']}";
        if hsh not in visited:
            visited.add(hsh)
            print(f"{subreq['pid1']}_{subreq['mid1']} -> {subreq['pid2']}_{subreq['mid2']} ({subreq['type_id']});")
            process_req(subreq['pid2'], subreq['mid2'], subreq['type_id'], level+1, depth)


def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    req_timelines.py: Display Motr request sequence diagram.
    """)
    parser.add_argument("-p", "--pid", type=int, default=None,
                        help="Process ID of client issued a request")
    parser.add_argument("-m", "--maximize", action='store_true', help="Display in maximised window")
    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-e", "--depth", type=int, default=20,
                        help="Display the first E lines in depth of client request")
    parser.add_argument("-s", "--sort", action='store_true',
                        help="Sort timelines by appearance time")
    parser.add_argument("request_id", type=str, help="Request id")

    parser.add_argument("--output-file", type=str, default=None,
                        help="Save picture of timelines into file")
    parser.add_argument("--no-window", action='store_true',
                        help="Don't show interactive window")

    return parser.parse_args()


def validate_args(args):
    if not args.pid:
        print("Process ID is not specified")
    if args.depth < 0:
        print("Request depth must be >= 0")
        sys.exit(-1)

if __name__ == '__main__':
    args = parse_args()
    validate_args(args)
    db_init(args.db)
    db_connect()
    pid = args.pid
    rid = args.request_id

    if not args.pid:
        req = relation.select().where(relation.mid1 == rid)
    else:
        req = relation.select().where((relation.pid1 == pid) & (relation.mid1 == rid))
    req_d = [r for r in req.dicts()]

    if not req_d:
        print(f"Requested pid {pid}, id {rid} doesn't exist")
        sys.exit(-1)

    print(f"Process pid {pid}, id {rid}")
    process_req(req_d[0]['pid1'], req_d[0]['mid1'], "client", 0, args.depth)

    ref_time = prepare_time_table(time_table, args.sort)
    draw_timelines(time_table, None, ref_time, 0, "ms", False, args.maximize,
                   no_window=args.no_window, filename=args.output_file)

    db_close()
