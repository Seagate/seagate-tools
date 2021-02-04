#
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
    parser.add_argument("request_id", type=str, help="Request id")

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

    ref_time = prepare_time_table(time_table)
    draw_timelines(time_table, None, ref_time, 0, "ms", False, args.maximize)

    db_close()
