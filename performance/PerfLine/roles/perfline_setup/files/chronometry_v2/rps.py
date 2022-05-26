#!/usr/bin/env python3
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates
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
# For any questions about this software or licensing,
# please email opensource@seagate.com or cortx-questions@seagate.com.

import pandas as pd
from pandas.io import sql
import gc
import sys
import argparse
from sys_utils import Figure, Queue, RPS, Layer, Relation, XIDRelation, \
    S3, MOTR_REQ, CRPC, SRPC, CAS, FOM, STIO, BETX,  S3PUT_FILTER, DIX, \
    Connection, S3GET_FILTER, S3_TO_CLIENT, IOO, CLIENT_TO_IOO, COB, \
    IOO_TO_CRPC, CLIENT_TO_COB, CLIENT_TO_DIX, DIX_TO_MDIX, DIX_TO_CAS, \
    COB_TO_CRPC, CAS_TO_CRPC, SRPC_TO_FOM, FOM_TO_STIO, FOM_TO_TX

class LocalFigure():
    def __init__(self, fig):
        self.fig = fig
        self.sharex = None

class Handler():
    NUM_CLI_LAYERS = 3 # S3, MOTR, CRPC
    NUM_SRV_LAYERS = 4 # SRPC, FOM, BETX, STIO
    NUM_COLS       = 2 # Queue and RPS
    SRV_IDX_OFFSET = 3

    def __init__(self, fiter, avg_window, save_only, hostmap=None):
        self.cluster_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide RPS',
                                              self.NUM_CLI_LAYERS + self.NUM_SRV_LAYERS,
                                              self.NUM_COLS))
        self.client_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide client RPS',
                                             self.NUM_CLI_LAYERS, self.NUM_COLS))
        self.server_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide server RPS',
                                             self.NUM_SRV_LAYERS, self.NUM_COLS))
        self.client_hosts = dict()
        self.server_hosts = dict()
        self.client_process = dict()
        self.server_process = dict()
        self.hostmap = hostmap
        self.save_only = save_only
        self.avg_window = avg_window
        self.fiter = fiter

    @staticmethod
    def draw_layer(fig, ypos, layer, start, stop, avg, pids,
                   sharex=None, samex=False):
        queue = Queue(layer, start, stop, pids=pids)
        rps_in = RPS(layer, start, color='green',
                     avg_window=avg, pids=pids)
        rps_out = RPS(layer, stop, color='red',
                      avg_window=avg, pids=pids)
        queue.calculate()
        rps_in.calculate()
        rps_out.calculate()

        axq = fig.add(queue, ypos, 0, sharex=sharex)
        if samex:
            sharex = axq
        axi = fig.add(rps_in, ypos, 1, sharex=sharex)
        axo = fig.add(rps_out, ypos, 1, sharex=sharex)
        return (axq, axi, axo)

    def process_s3(self, layer):
        (axq, axi, axo) = self.draw_layer(self.cluster_agg.fig, 0, layer,
                                          ["START"], ["COMPLETE"],
                                          self.avg_window, None, samex=True)
        axq.set_title("Queue length")
        axi.set_title(f"Requests per second, avg_window {self.avg_window}")
        self.cluster_agg.sharex = axq

        (axq, axi, axo) = self.draw_layer(self.client_agg.fig, 0, layer,
                                          ["START"], ["COMPLETE"],
                                          self.avg_window, None, samex=True)
        axq.set_title("Queue length")
        axi.set_title(f"Requests per second, avg_window {self.avg_window}")
        self.client_agg.sharex = axq

        pids = layer.pids()
        for pid in pids:
            lfig = LocalFigure(Figure(f'{self.fiter.name} process {pid} client RPS',
                                     self.NUM_CLI_LAYERS, self.NUM_COLS))
            self.client_process[pid] = lfig
            (axq, axi, axo) = self.draw_layer(lfig.fig, 0, layer,
                                              ["START"], ["COMPLETE"],
                                              self.avg_window, [pid], samex=True)
            axq.set_title("Queue length")
            axi.set_title(f"Requests per second, avg_window {self.avg_window}")
            lfig.sharex = axq

        if self.hostmap is not None:
            for host in self.hostmap.keys():
                title = f'{self.fiter.name} node {host} client RPS'
                lfig = LocalFigure(Figure(title,
                                          self.NUM_CLI_LAYERS, self.NUM_COLS))
                self.client_hosts[host] = lfig
                (axq, axi, axo) = self.draw_layer(lfig.fig, 0, layer,
                                                  ["START"], ["COMPLETE"],
                                                  self.avg_window,
                                                  self.hostmap[host], samex=True)

                axq.set_title("Queue length")
                axi.set_title(f"Requests per second, avg_window {self.avg_window}")
                lfig.sharex = axq

    def process_client(self, layer, start, stop, ypos):
        (axq, axi, axo) = self.draw_layer(self.cluster_agg.fig, ypos, layer,
                                          start, stop, self.avg_window, None,
                                          sharex=self.cluster_agg.sharex)

        (axq, axi, axo) = self.draw_layer(self.client_agg.fig, ypos, layer,
                                          start, stop, self.avg_window, None,
                                          sharex=self.client_agg.sharex)

        pids = self.client_process.keys()
        for pid in pids:
            lfig = self.client_process[pid]
            (axq, axi, axo) = self.draw_layer(lfig.fig, ypos, layer,
                                              start, stop, self.avg_window, [pid],
                                              lfig.sharex)

        if self.hostmap is not None:
            for host in self.hostmap.keys():
                lfig = self.client_hosts[host]
                (axq, axi, axo) = self.draw_layer(lfig.fig, ypos, layer,
                                                  start, stop, self.avg_window,
                                                  self.hostmap[host], lfig.sharex)

    def process_srpc(self, layer, start, stop, ypos):
        (axq, axi, axo) = self.draw_layer(self.cluster_agg.fig, ypos, layer,
                                          start, stop, self.avg_window, None,
                                          sharex=self.cluster_agg.sharex)

        (axq, axi, axo) = self.draw_layer(self.server_agg.fig,
                                          ypos - self.SRV_IDX_OFFSET,
                                          layer, start, stop, self.avg_window,
                                          None, samex=True)
        axq.set_title("Queue length")
        axi.set_title(f"Requests per second, avg_window {self.avg_window}")
        self.server_agg.sharex = axq

        pids = layer.pids()
        for pid in pids:
            lfig = LocalFigure(Figure(f'{self.fiter.name} process {pid} server RPS',
                                     self.NUM_SRV_LAYERS, self.NUM_COLS))
            self.server_process[pid] = lfig
            (axq, axi, axo) = self.draw_layer(lfig.fig,
                                              ypos - self.SRV_IDX_OFFSET,
                                              layer, start, stop, self.avg_window,
                                              [pid], samex=True)
            axq.set_title("Queue length")
            axi.set_title(f"Requests per second, avg_window {self.avg_window}")
            lfig.sharex = axq

        if self.hostmap is not None:
            for host in self.hostmap.keys():
                title = f'{self.fiter.name} node {host} server RPS'
                lfig = LocalFigure(Figure(title,
                                          self.NUM_SRV_LAYERS, self.NUM_COLS))
                self.server_hosts[host] = lfig
                (axq, axi, axo) = self.draw_layer(lfig.fig,
                                                  ypos - self.SRV_IDX_OFFSET,
                                                  layer, start, stop,
                                                  self.avg_window,
                                                  self.hostmap[host], samex=True)

                axq.set_title("Queue length")
                axi.set_title(f"Requests per second, avg_window {self.avg_window}")
                lfig.sharex = axq


    def process_server(self, layer, start, stop, ypos):
        (axq, axi, axo) = self.draw_layer(self.cluster_agg.fig, ypos, layer,
                                          start, stop, self.avg_window, None,
                                          sharex=self.cluster_agg.sharex)

        (axq, axi, axo) = self.draw_layer(self.server_agg.fig,
                                          ypos - self.SRV_IDX_OFFSET,
                                          layer, start, stop, self.avg_window, None,
                                          sharex=self.server_agg.sharex)

        pids = self.server_process.keys()
        for pid in pids:
            lfig = self.server_process[pid]
            (axq, axi, axo) = self.draw_layer(lfig.fig,
                                              ypos - self.SRV_IDX_OFFSET,
                                              layer, start, stop, self.avg_window,
                                              [pid], sharex=lfig.sharex)

        if self.hostmap is not None:
            for host in self.hostmap.keys():
                lfig = self.server_hosts[host]
                (axq, axi, axo) = self.draw_layer(lfig.fig,
                                                  ypos - self.SRV_IDX_OFFSET,
                                                  layer, start, stop,
                                                  self.avg_window,
                                                  self.hostmap[host], lfig.sharex)

    def consume(self, layer):
        if layer.layer_type == S3:
            self.process_s3(layer)
        if layer.layer_type == MOTR_REQ:
            self.process_client(layer, ["initialised"], ['stable'], 1)
        if layer.layer_type == CRPC:
            self.process_client(layer, ['INITIALISED'], ['REPLIED'], 2)
        if layer.layer_type == SRPC:
            self.process_srpc(layer, ['INITIALISED'], ['REPLIED'], 3)
        if layer.layer_type == FOM:
            self.process_server(layer, ['0', '-1'], ['finish'], 4)
        if layer.layer_type == STIO:
            self.process_server(layer, ['M0_AVI_IO_LAUNCH'], ['M0_AVI_AD_ENDIO'], 5)
        if layer.layer_type == BETX:
            self.process_server(layer, ['prepare'], ['done'], 6)

    def done(self):
        self.cluster_agg.fig.draw()
        self.cluster_agg.fig.save()

        self.client_agg.fig.draw()
        self.client_agg.fig.save()

        self.server_agg.fig.draw()
        self.server_agg.fig.save()

        for pid in self.client_process.keys():
            fig = self.client_process[pid].fig
            fig.draw()
            fig.save()

        for pid in self.server_process.keys():
            fig = self.server_process[pid].fig
            fig.draw()
            fig.save()

        for host in self.client_hosts:
            fig = self.client_hosts[host].fig
            fig.draw()
            fig.save()

        for host in self.server_hosts:
            fig = self.server_hosts[host].fig
            fig.draw()
            fig.save()

        if not self.save_only:
            self.cluster_agg.fig.show()

def pandas_init():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

def pandas_fini():
    pass

def calculate(conn, fiter, handler):
    s3all = Layer(S3, conn)
    s3 = fiter.run(s3all)
    handler.consume(s3)
    del s3all
    gc.collect()

    rel = Relation(S3_TO_CLIENT, conn)
    motr_all = Layer(MOTR_REQ, conn)
    motr = rel.sieve(s3, motr_all)
    handler.consume(motr)

    del rel
    del motr_all
    del s3
    gc.collect()

    ioo_all = Layer(IOO, conn)
    rel = Relation(CLIENT_TO_IOO, conn)
    ioo = rel.sieve(motr, ioo_all)
    del ioo_all
    del rel
    gc.collect()

    cob_all = Layer(COB, conn)
    rel = Relation(CLIENT_TO_COB, conn)
    cob = rel.sieve(motr, cob_all)
    del cob_all
    del rel
    gc.collect()

    dix_all = Layer(DIX, conn)
    rel_dix = Relation(CLIENT_TO_DIX, conn)
    rel_mdix = Relation(DIX_TO_MDIX, conn)
    dix = rel_dix.sieve(motr, dix_all)
    mdix = rel_mdix.sieve(dix, dix_all)

    cas_all = Layer(CAS, conn)
    rel_cas = Relation(DIX_TO_CAS, conn)
    cas = rel_cas.sieve(dix, cas_all)
    cas2 = rel_cas.sieve(mdix, cas_all)
    cas.merge(cas2)

    del dix_all
    del cas_all
    del mdix
    del dix
    del rel_dix
    del rel_mdix
    gc.collect()

    rpc_all = Layer(CRPC, conn)
    rel_ioo = Relation(IOO_TO_CRPC, conn)
    rel_cob = Relation(COB_TO_CRPC, conn)
    rel_cas = Relation(CAS_TO_CRPC, conn)
    crpc_ioo = rel_ioo.sieve(ioo, rpc_all)
    crpc_cob = rel_cob.sieve(cob, rpc_all)
    crpc_cas = rel_cas.sieve(cas, rpc_all)

    crpc = crpc_ioo
    crpc.merge(crpc_cob)
    crpc.merge(crpc_cas)

    del rel_ioo
    del rel_cob
    del rel_cas
    del crpc_ioo
    del crpc_cob
    del crpc_cas

    handler.consume(crpc)

    del rpc_all

    rpc_all = Layer(SRPC, conn)
    rel = XIDRelation(conn)
    srpc = rel.sieve(crpc, rpc_all)

    del rpc_all
    del crpc

    handler.consume(srpc)

    fom_all = Layer(FOM, conn)
    rel = Relation(SRPC_TO_FOM, conn)
    fom = rel.sieve(srpc, fom_all)
    del rel
    del srpc
    del fom_all
    gc.collect()

    handler.consume(fom)

    stio_all = Layer(STIO, conn)
    rel = Relation(FOM_TO_STIO, conn)
    stio = rel.sieve(fom, stio_all)

    del stio_all
    del rel
    gc.collect()

    handler.consume(stio)
    del stio

    # Only for writes
    if fiter is S3PUT_FILTER:
        betx_all = Layer(BETX, conn)
        rel = Relation(FOM_TO_TX, conn)
        betx = rel.sieve(fom, betx_all)

        del betx_all
        del fom
        del rel
        gc.collect()

        handler.consume(betx)
        del betx

    handler.done()

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    rps.py: Generate request per second plots of Cortx S3 and Motr layers
    """)

    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-g",'--s3get', action='store_true',
                        help="Show histograms of S3GetObject operation")
    parser.add_argument("-p", "--s3put", action='store_true',
                        help="Show histograms of S3GetObject operation")
    parser.add_argument("-s", "--save-only", action='store_true',
                        help="Don't show figures, only save")
    parser.add_argument("-w", "--avg-window", type=str, default='1s',
                        help="Rolling window duration, default '1s'")

    args = parser.parse_args()

    return args

def get_hosts_pids(conn):
    table_descr_query = 'select * from sqlite_master where type="table" and name="host"'
    table_descr_df = sql.read_sql(table_descr_query, con=conn.conn)

    if table_descr_df.empty:
        return None

    pids_df = sql.read_sql('select * from host', con=conn.conn)

    if pids_df.empty:
        return None

    pids_df = pids_df.drop_duplicates(subset=['pid'])
    hostmap = pids_df.groupby('hostname')['pid'].apply(list).to_dict()
    return hostmap

def main():
    args = parse_args()

    pandas_init()

    conn = Connection(args.db)
    conn.connect()

    if not args.s3get and not args.s3put:
        args.s3get = True
        args.s3put = True

    hostmap = get_hosts_pids(conn)

    if args.s3put:
        handler = Handler(S3PUT_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap)
        calculate(conn, S3PUT_FILTER, handler)

    if args.s3get:
        handler = Handler(S3GET_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap)
        calculate(conn, S3GET_FILTER, handler)

    return

if __name__ == "__main__":
    main()

