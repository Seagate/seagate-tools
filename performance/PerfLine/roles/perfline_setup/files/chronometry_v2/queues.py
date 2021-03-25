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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io import sql
import sqlite3
import sys
import argparse

def pandas_init():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)

def pandas_fini():
    pass

def get_aggregated_pids(db_connection):
    result = []
    all_pids_df = sql.read_sql('select distinct(pid) from request', con=db_connection)
    result.append( ('AGGR', all_pids_df) )
    return result

def get_hosts_pids(db_connection):
    table_descr_query = 'select * from sqlite_master where type="table" and name="host"'
    table_descr_df = sql.read_sql(table_descr_query, con=db_connection)

    if table_descr_df.empty:
        return None

    pids_df = sql.read_sql('select * from host', con=db_connection)

    if pids_df.empty:
        return None

    pids_df = pids_df.drop_duplicates()
    hosts_df = pids_df[ ['hostname'] ].drop_duplicates()
    result = []

    for index, row in hosts_df.iterrows():
        hostname = row['hostname']
        host_pids_df = pids_df[ pids_df.hostname == hostname ][ ['pid'] ]
        result.append( (hostname, host_pids_df) )

    return result

def layout_init(cli_rows_nr, srv_rows_nr, cols_nr, is_cli_aggr, is_srv_aggr, title):
    rows = cli_rows_nr + srv_rows_nr
    axes = []
    fig = plt.figure(figsize=(10, 10))
    layout = fig.add_gridspec(rows, cols_nr)

    ax = None 
    for i in range(0, rows):
        axes.append([])

        if i < cli_rows_nr:
            #client
            if is_cli_aggr:
                ax = fig.add_subplot(layout[i, :], sharex=ax)
                axes[i].append(ax)
            else:
                for j in range(0, cols_nr):
                    ax = fig.add_subplot(layout[i, j], sharex=ax)
                    axes[i].append(ax)
        else:
            #server
            if is_srv_aggr:
                ax = fig.add_subplot(layout[i, :], sharex=ax)
                axes[i].append(ax)
            else:
                for j in range(0, cols_nr):
                    ax = fig.add_subplot(layout[i, j], sharex = ax)
                    axes[i].append(ax)

    plt.suptitle(title)
    return axes

def layout_fini():
    plt.gcf().align_ylabels()
    plt.show()

def connect(db_path):
    return sqlite3.connect(db_path)

def disconnect(db_connection):
    db_connection.close()

def queue(df, start_states, stop_states, label):
    df = df[(df.state.isin(start_states)) | (df.state.isin(stop_states))]
    df = df[['time','state']]
    df.set_index('time', inplace=True)

    replace_rule = dict()

    for start_state in start_states:
        replace_rule[start_state] = 1

    for stop_state in stop_states:
        replace_rule[stop_state] = -1

    df = df.replace(replace_rule)
    df = df.sort_values('time').cumsum()
    df.rename(columns={"state": label}, inplace=True)
    df.index = [pd.Timestamp(x, unit='ns') for x in df.index]
    return df

def plot(df, ax=None, label=None, color='b', title=None):
    ax = df.plot(alpha=0.5, ax=ax, color=color, grid=True)
    ax.legend(loc="upper right")
    return ax

def s3reqs(conn):
    query = 'SELECT * FROM request where type_id like "%s3_request_state%"'
    return sql.read_sql(query, con=conn)
    
def s3states(df, state):
    mask = df[df.state.str.contains(state)][['pid', 'id']].drop_duplicates()
    return pd.merge(df, mask, on=['pid', 'id'], how='inner')

def s3_queue(conn, ax, hosts, show_title):
    start = ['START']
    stop = ['COMPLETE']
    ax[0].set_ylabel('S3')

    s3 = s3reqs(conn)
    s3p = s3states(s3, 'S3PutObjectAction')
    s3g = s3states(s3, 'S3GetObjectAction')

    for i, (host, pids_df) in enumerate(hosts):
        s3p_host = pd.merge(s3p, pids_df, on=['pid'], how='inner')
        s3g_host = pd.merge(s3g, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(s3p_host, start, stop, label="S3 Put"), ax=ax[i], color='r')
        plot(queue(s3g_host, start, stop, label="S3 Get"), ax=ax[i], color='g')

def client_req(conn, operation):
    query = f'''
    SELECT
    client.time as time, client.pid as pid, client.id as id, client.state as state
    FROM request client
    JOIN attr ON client.pid=attr.pid and client.id=attr.entity_id
    WHERE 
    attr.val="{operation}" AND
    client.type_id="client_req"
    '''
    
    df = sql.read_sql(query, con=conn)
    df = df.drop_duplicates()
    return df

def client_req_queue(conn, ax, hosts, show_title):
    start = ['initialised']
    stop = ['stable']
    opcode = 'M0_OC_WRITE'
    ax[0].set_ylabel('MOTR CLIENT')

    writes = client_req(conn, 'M0_OC_WRITE')
    reads = client_req(conn, 'M0_OC_READ')

    for i, (host, pids_df) in enumerate(hosts):
        writes_host = pd.merge(writes, pids_df, on=['pid'], how='inner')
        reads_host = pd.merge(reads, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(writes_host, start, stop, label="Write"), ax=ax[i], color='r')
        plot(queue(reads_host, start, stop, label="Read"), ax=ax[i], color='g')

def crpc_writev_req(conn):
    query = f'''
    SELECT
    crpc.time as time, crpc.pid as pid, crpc.id as id, crpc.state as state
    FROM request crpc
    JOIN attr ON crpc.pid=attr.pid and crpc.id=attr.entity_id
    WHERE 
    (attr.val="M0_IOSERVICE_WRITEV_OPCODE" OR attr.val="M0_IOSERVICE_COB_CREATE_OPCODE") AND
    crpc.type_id="rpc_req"
    '''
    
    df = sql.read_sql(query, con=conn)
    df = df.drop_duplicates()
    return df

def crpc_readv_req(conn):
    query = f'''
    SELECT
    crpc.time as time, crpc.pid as pid, crpc.id as id, crpc.state as state
    FROM request crpc
    JOIN attr ON crpc.pid=attr.pid and crpc.id=attr.entity_id
    WHERE 
    attr.val="M0_IOSERVICE_READV_OPCODE" AND
    crpc.type_id="rpc_req"
    '''
    
    df = sql.read_sql(query, con=conn)
    df = df.drop_duplicates()
    return df

def crpc_queue(conn, ax, hosts, show_title):
    start = ['INITIALISED']
    stop = ['REPLIED']
    ax[0].set_ylabel('CRPC')

    writev = crpc_writev_req(conn)
    readv = crpc_readv_req(conn)

    for i, (host, pids_df) in enumerate(hosts):
        writev_host = pd.merge(writev, pids_df, on=['pid'], how='inner')
        readv_host = pd.merge(readv, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(writev_host, start, stop, label="Writev"), ax=ax[i], color='r')
        plot(queue(readv_host, start, stop, label="Readv"), ax=ax[i], color='g')

def srpc_queue(conn, ax, hosts, show_title):
    start = ["ACCEPTED"]
    stop = ["REPLIED", "FAILED"]
    ax[0].set_ylabel('SRPC')

    query = 'SELECT * FROM request where type_id="rpc_req"'
    srpc_df = sql.read_sql(query, con=conn)

    sxid_query = 'SELECT * FROM relation WHERE type_id="sxid_to_rpc"'
    sxid_df = sql.read_sql(sxid_query, con=conn)

    sxid_df = sxid_df[ ['pid1', 'mid1', 'pid2', 'mid2'] ].rename(columns={"pid2": "pid", "mid2": "id"})

    sxid_srpc_df = pd.merge(srpc_df, sxid_df, on=['pid', 'id'], how='inner')

    unique_srpc_df = sxid_srpc_df.sort_values('time').drop_duplicates(subset=['pid1', 'mid1'], keep='first')
    unique_srpc_df = unique_srpc_df[ ['pid', 'id'] ]

    srpc_df = pd.merge(srpc_df, unique_srpc_df, on=['pid', 'id'], how='inner')

    srpc_mask = srpc_df[srpc_df.state.str.contains("ACCEPTED")][['pid', 'id']].drop_duplicates()
    srpc_df = pd.merge(srpc_df, srpc_mask, on=['pid', 'id'], how='inner')

    for i, (host, pids_df) in enumerate(hosts):
        srpc_df_host = pd.merge(srpc_df, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(srpc_df_host, start, stop, label="SRPC"), ax=ax[i], color='r')

def fom_queue(conn, ax, hosts, show_title):
    start = ['-1']
    stop = ['finish']
    ax[0].set_ylabel('FOM')
    opcodes_query = "SELECT * FROM attr where attr.name='req-opcode'"
    opcodes_df = sql.read_sql(opcodes_query, con=conn)

    read_opcodes_df = opcodes_df[opcodes_df.val.str.contains("READV")][ ['entity_id', 'pid'] ].rename(columns={"entity_id": "id"})
    write_opcodes_df = opcodes_df[opcodes_df.val.str.contains("WRITEV")][ ['entity_id', 'pid'] ].rename(columns={"entity_id": "id"})

    fom_query = "SELECT * FROM request WHERE type_id='fom_req'"
    fom_df = sql.read_sql(fom_query, con=conn)

    read_foms_df = pd.merge(fom_df, read_opcodes_df, on=['pid', 'id'], how='inner')
    write_foms_df = pd.merge(fom_df, write_opcodes_df, on=['pid', 'id'], how='inner')

    for i, (host, pids_df) in enumerate(hosts):
        read_foms_df_host = pd.merge(read_foms_df, pids_df, on=['pid'], how='inner')
        write_foms_df_host = pd.merge(write_foms_df, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(read_foms_df_host, start, stop, label="FOM_READ"), ax=ax[i], color='g')
        plot(queue(write_foms_df_host, start, stop, label="FOM_WRITE"), ax=ax[i], color='r')

def be_queue(conn, ax, hosts, show_title):
    start = ['prepare']
    stop = ['done']
    ax[0].set_ylabel('BE')
    tx_query = "SELECT * FROM request WHERE type_id='be_tx'"
    tx_df = sql.read_sql(tx_query, con=conn)

    for i, (host, pids_df) in enumerate(hosts):
        tx_df_host = pd.merge(tx_df, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(tx_df_host, start, stop, label="TX"), ax=ax[i], color='r')

def stio_queue(conn, ax, hosts, show_title):
    start = ['M0_AVI_AD_PREPARE']
    stop = ['M0_AVI_AD_ENDIO']
    ax[0].set_ylabel('STOBIO')
    stio_query = "SELECT * FROM request WHERE type_id='stio_req'"
    stio_df = sql.read_sql(stio_query, con=conn)

    stio_write_mask = stio_df[stio_df.state.str.contains('M0_AVI_AD_WR_PREPARE')][ ['pid', 'id'] ].drop_duplicates()
    
    stio_write_mask['is_write'] = 1
    stio_df = pd.merge(stio_df, stio_write_mask, on=['pid', 'id'], how='left')
    stio_write_df = stio_df[ (stio_df["is_write"] == 1) ]
    stio_read_df = stio_df[ (stio_df["is_write"] != 1) ]

    for i, (host, pids_df) in enumerate(hosts):
        stio_write_df_host = pd.merge(stio_write_df, pids_df, on=['pid'], how='inner')
        stio_read_df_host = pd.merge(stio_read_df, pids_df, on=['pid'], how='inner')

        if show_title:
            ax[i].set_title(f'{host}')

        plot(queue(stio_write_df_host, start, stop, label="STIO Write"), ax=ax[i], color='r')
        plot(queue(stio_read_df_host, start, stop, label="STIO Read"), ax=ax[i], color='g')

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    queues.py: Display Cortx request queues.
    """)
    
    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-a", "--aggregated-cli", action='store_true',
                        help="Show client queues from data collected from all nodes")
    parser.add_argument("-b", "--aggregated-srv", action='store_true',
                        help="Show server queues from data collected from all nodes")

    return parser.parse_args()

def main():
    args = parse_args()
    layers_cli = [s3_queue, client_req_queue, crpc_queue]
    layers_srv = [srpc_queue, fom_queue, be_queue, stio_queue]
    pandas_init()
    
    conn = connect(args.db)

    aggregated_pids = get_aggregated_pids(conn)
    hosts_pids = get_hosts_pids(conn)

    if hosts_pids is None:
        hosts_pids = aggregated_pids
    
    cli_aggr = args.aggregated_cli
    srv_aggr = args.aggregated_srv
    
    show_srv_title = False
    show_cli_title = False

    if not cli_aggr:
        show_cli_title = True
    elif not srv_aggr:
        show_srv_title = True

    axes = layout_init(len(layers_cli), len(layers_srv), len(hosts_pids),
                       cli_aggr, srv_aggr, "S3/Motr queues")

    cli_hosts = aggregated_pids if cli_aggr else hosts_pids

    for i, layer in enumerate(layers_cli):
        print("drawing {} ".format(layer.__name__))
        layer(conn, axes[i], cli_hosts, show_cli_title)
        show_cli_title = False

    srv_hosts = aggregated_pids if srv_aggr else hosts_pids

    for i, layer in enumerate(layers_srv):
        print("drawing {} ".format(layer.__name__))
        layer(conn, axes[i + len(layers_cli)], srv_hosts, show_srv_title)
        show_srv_title = False

    layout_fini()
    disconnect(conn)
    return

if __name__ == "__main__":
    main()
