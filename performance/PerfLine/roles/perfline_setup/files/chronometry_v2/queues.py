#!/usr/bin/env python3

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

def layout_init(rows, cols, title):
    axes = []
    fig = plt.figure(figsize=(10, 10))
    layout = fig.add_gridspec(rows, cols)

    ax = None 
    for i in range(0, rows):
        ax = fig.add_subplot(layout[i, 0], sharex = ax)
        axes.append(ax)
    plt.suptitle(title)

    return axes

def layout_fini():
    plt.show()

def connect(db_path):
    return sqlite3.connect(db_path)

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

def s3_queue(conn, ax):
    start = ['START']
    stop = ['COMPLETE']

    s3 = s3reqs(conn)
    s3p = s3states(s3, 'S3PutObjectAction')
    s3g = s3states(s3, 'S3GetObjectAction')

    ax.set_title('S3 layer [S3:START->S3:COMPLETE]')
    plot(queue(s3p, start, stop, label="S3 Put"), ax=ax, color='r')
    plot(queue(s3g, start, stop, label="S3 Get"), ax=ax, color='g')

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

def client_req_queue(conn, ax):
    start = ['initialised']
    stop = ['stable']
    opcode = 'M0_OC_WRITE'

    writes = client_req(conn, 'M0_OC_WRITE')
    reads = client_req(conn, 'M0_OC_READ')

    ax.set_title(f'Motr client [client_req:{start}->client_req:{stop}]')
    plot(queue(writes, start, stop, label="Write"), ax=ax, color='r')
    plot(queue(reads, start, stop, label="Read"), ax=ax, color='g')

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

def crpc_queue(conn, ax):
    start = ['INITIALISED']
    stop = ['REPLIED']

    writev = crpc_writev_req(conn)
    readv = crpc_readv_req(conn)

    ax.set_title(f'CRPC [CRPC:{start}->CRPC:{stop}]')
    plot(queue(writev, start, stop, label="Writev"), ax=ax, color='r')
    plot(queue(readv, start, stop, label="Readv"), ax=ax, color='g')

def srpc_queue(conn, ax):
    start = ["ACCEPTED"]
    stop = ["REPLIED", "FAILED"]

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

    ax.set_title('SRPC layer [ACCEPTED->REPLIED]')
    plot(queue(srpc_df, start, stop, label="SRPC"), ax=ax, color='r')

def fom_queue(conn, ax):
    start = ['-1']
    stop = ['finish']
    opcodes_query = "SELECT * FROM attr where attr.name='req-opcode'"
    opcodes_df = sql.read_sql(opcodes_query, con=conn)

    read_opcodes_df = opcodes_df[opcodes_df.val.str.contains("READV")][ ['entity_id', 'pid'] ].rename(columns={"entity_id": "id"})
    write_opcodes_df = opcodes_df[opcodes_df.val.str.contains("WRITEV")][ ['entity_id', 'pid'] ].rename(columns={"entity_id": "id"})

    fom_query = "SELECT * FROM request WHERE type_id='fom_req'"
    fom_df = sql.read_sql(fom_query, con=conn)

    read_foms_df = pd.merge(fom_df, read_opcodes_df, on=['pid', 'id'], how='inner')
    write_foms_df = pd.merge(fom_df, write_opcodes_df, on=['pid', 'id'], how='inner')

    ax.set_title('FOM layer [-1->finish]')
    plot(queue(read_foms_df, start, stop, label="FOM_READ"), ax=ax, color='g')
    plot(queue(write_foms_df, start, stop, label="FOM_WRITE"), ax=ax, color='r')

def be_queue(conn, ax):
    start = ['prepare']
    stop = ['done']
    tx_query = "SELECT * FROM request WHERE type_id='be_tx'"
    tx_df = sql.read_sql(tx_query, con=conn)
    ax.set_title('BE layer [prepare -> done]')
    plot(queue(tx_df, start, stop, label="TX"), ax=ax, color='r')


def stio_queue(conn, ax):
    start = ['M0_AVI_AD_PREPARE']
    stop = ['M0_AVI_AD_ENDIO']
    stio_query = "SELECT * FROM request WHERE type_id='stio_req'"
    stio_df = sql.read_sql(stio_query, con=conn)

    stio_write_mask = stio_df[stio_df.state.str.contains('M0_AVI_AD_WR_PREPARE')][ ['pid', 'id'] ].drop_duplicates()
    
    stio_write_mask['is_write'] = 1
    stio_df = pd.merge(stio_df, stio_write_mask, on=['pid', 'id'], how='left')
    stio_write_df = stio_df[ (stio_df["is_write"] == 1) ]
    stio_read_df = stio_df[ (stio_df["is_write"] != 1) ]


    ax.set_title('STOB layer [M0_AVI_AD_PREPARE -> M0_AVI_AD_ENDIO]')
    plot(queue(stio_write_df, start, stop, label="STIO Write"), ax=ax, color='r')
    plot(queue(stio_read_df, start, stop, label="STIO Read"), ax=ax, color='g')

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    queues.py: Display Cortx request queues.
    """)
    
    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")

    return parser.parse_args()

def main():
    args = parse_args()

    layers = [s3_queue, client_req_queue, crpc_queue,
              srpc_queue, fom_queue, be_queue,
              stio_queue]

    pandas_init()
    axes = layout_init(len(layers), 1, "S3/Motr queues")
    conn = connect(args.db)

    for i, layer in enumerate(layers):
        print("drawing {} ".format(layer.__name__))
        layer(conn, axes[i])

    layout_fini()
    return

if __name__ == "__main__":
    main()
