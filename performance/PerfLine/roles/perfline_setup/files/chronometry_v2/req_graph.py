#!/usr/bin/env python3
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
from req_utils import query2dlist
import sys
from graphviz import Digraph

time_table = []
visited = set()
NODE_TEMPLATE="""<
<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4">
  <TR>
    <TD>{}</TD>
  </TR>
  <TR>
    <TD>{}</TD>
  </TR>
</TABLE>>
"""

def add_node(digraph, node_name, node_header, attrs):
    label = "<BR/>".join([f"{k}={v}" for (k,v) in attrs.items()])
    digraph.node(node_name, NODE_TEMPLATE.format(node_header, label))

def add_link(digraph, first_node_name, second_node_name):
    digraph.edge(first_node_name, second_node_name)

def get_req_attrs(pid, rid):
    c = lambda attr: re.sub("M0_AVI_.*_ATTR_", "", attr)
    attrd = query2dlist(attr.select().where( (attr.entity_id==rid)
                                            &(attr.pid==pid)))
    attrs = dict([(c(a['name']), a['val']) for a in attrd])
    return attrs

def process_req(pid, rid, type_id, level, depth, digraph, parent_name = None):
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
    graph_node_name = parent_name
    requests_d = query2dlist(request.select().where((request.id==rid) & (request.pid==pid)))
    if requests_d:
        op = requests_d[0]['type_id']
        graph_node_name=f"{op}__pid={pid}__id={rid}"
        node_header = f"{op}: pid={pid}, id={rid}"
        attrs = get_req_attrs(pid, rid)
        add_node(digraph, graph_node_name, node_header, attrs)
        if parent_name:
            add_link(digraph, parent_name, graph_node_name)

    # Check depth
    if level >= depth:
        return
    
    # Traverse children
    for subreq in subreqs:
        hsh = f"{subreq['pid2']}_{subreq['mid2']}";
        if hsh not in visited:
            visited.add(hsh)
            print(f"{subreq['pid1']}_{subreq['mid1']} -> {subreq['pid2']}_{subreq['mid2']} ({subreq['type_id']});")
            process_req(subreq['pid2'], subreq['mid2'], subreq['type_id'], level+1, depth, digraph, graph_node_name)

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    req_graph.py: Display Cortx request graph.
    """)
    parser.add_argument("-p", "--pid", type=int, default=None,
                        help="Process ID of client issued a request")
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

    digraph = Digraph(strict=True, format='png', node_attr = {'shape': 'plaintext'})
    process_req(req_d[0]['pid1'], req_d[0]['mid1'], "client", 0, args.depth, digraph)
    digraph.render(f'attr_graph_{pid}_{rid}')
    db_close()

