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

import pandas as pd
from pandas.io import sql
import gc
import sys
import argparse
from sys_utils import Figure, Latency, Queue, Layer, Relation, XIDRelation, \
    S3, MOTR_REQ, CRPC, SRPC, CAS, FOM, STIO, BETX,  S3PUT_FILTER, DIX, \
    Connection, S3GET_FILTER, S3_TO_CLIENT, IOO, CLIENT_TO_IOO, COB, \
    IOO_TO_CRPC, CLIENT_TO_COB, CLIENT_TO_DIX, DIX_TO_MDIX, DIX_TO_CAS, \
    COB_TO_CRPC, CAS_TO_CRPC, SRPC_TO_FOM, FOM_TO_STIO, FOM_TO_TX

from sys_utils import ADD_START_COMPLETE_RGW_REQ_FILTER, get_hosts_pids

class LocalFigure():
    def __init__(self, fig):
        self.fig = fig
        self.sharex = None

class Handler():
    NUM_CLI_LAYERS = 3 # S3, MOTR, CRPC
    NUM_SRV_LAYERS = 4 # SRPC, FOM, BETX, STIO
    NUM_COLS       = 2 # Queue and Latency

    def __init__(self, fiter, avg_window, save_only,
                 hostmap=None, agg=True,
                 per_host=False, per_process=True,
                 client=True, server=True):
        self.hostmap = hostmap
        self.save_only = save_only
        self.avg_window = avg_window
        self.fiter = fiter
        self.agg = agg
        self.per_host = per_host
        self.per_process = per_process
        self.client = client
        self.server = server
        if self.agg:
            self.cluster_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide latency',
                                                  self.NUM_CLI_LAYERS + self.NUM_SRV_LAYERS,
                                                  self.NUM_COLS))
        if self.agg and self.client:
            self.client_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide client latency',
                                                 self.NUM_CLI_LAYERS, self.NUM_COLS))

        if self.agg and self.server:
            self.server_agg = LocalFigure(Figure(f'{fiter.name} cluster-wide server latency',
                                                 self.NUM_SRV_LAYERS, self.NUM_COLS))

        self.client_hosts = dict()
        self.server_hosts = dict()

        if self.per_process and self.client:
            self.client_process = dict()
        if self.per_process and self.server:
            self.server_process = dict()

    @staticmethod
    def draw_layer(fig, ypos, layer, start, stop, avg, pids=None,
                   sharex=None, samex=False):
        queue = Queue(layer, start, stop, pids=pids)
        latency = Latency(layer, start, stop,
                          pids=pids, avg_window=avg, scale='ms')
        queue.calculate()
        latency.calculate()

        axq = fig.add(queue, ypos, 0, sharex=sharex)
        if samex:
            sharex = axq
        axl = fig.add(latency, ypos, 1, sharex=sharex)
        return (axq, axl)

    def draw(self, lfig, ypos, layer, start, stop,
             first_plot=False, pids=None):
        (axq, axl) = self.draw_layer(lfig.fig, ypos, layer,
                                     start, stop,
                                     self.avg_window, sharex=lfig.sharex,
                                     samex=first_plot, pids=pids)
        lfig.sharex = axq
        if first_plot:
            axq.set_title("Queue length")
            axl.set_title(f"Latency, ms, avg_window {self.avg_window}")

    def process_agg(self, layer, start, stop,
                    ypos_com, ypos_cli, ypos_srv):

        if self.agg and ypos_com is not None:
            self.draw(self.cluster_agg, ypos_com, layer,
                      start, stop, layer.layer_type == S3)

        if self.agg and self.client and ypos_cli is not None:
            self.draw(self.client_agg, ypos_cli, layer,
                      start, stop, layer.layer_type == S3)

        if self.agg and self.server and ypos_srv is not None:
            self.draw(self.server_agg, ypos_srv,
                      layer, start, stop, layer.layer_type == SRPC)

    def create_host_figs(self, container, rows, cols, label):
        if not container:
            for host in self.hostmap.keys():
                title = f'{self.fiter.name} node {host} {label} latency'
                lfig = LocalFigure(Figure(title, rows, cols))
                container[host] = lfig

    def process_per_host(self, layer, start, stop,
                         dummy, ypos_cli, ypos_srv):
        if self.hostmap and self.per_host and self.client and ypos_cli is not None:
            if len(self.client_hosts) == 0:
                self.create_host_figs(self.client_hosts,
                                      self.NUM_CLI_LAYERS,
                                      self.NUM_COLS,
                                      'client')
            for host in self.hostmap.keys():
                lfig = self.client_hosts[host]
                self.draw(lfig, ypos_cli,
                          layer, start, stop, layer.layer_type == S3,
                          pids=self.hostmap[host])

        if self.hostmap and self.per_host and self.server and ypos_srv is not None:
            if len(self.server_hosts) == 0:
                self.create_host_figs(self.server_hosts,
                                      self.NUM_SRV_LAYERS,
                                      self.NUM_COLS,
                                      'server')
            for host in self.hostmap.keys():
                lfig = self.server_hosts[host]
                self.draw(lfig, ypos_srv,
                          layer, start, stop, layer.layer_type == SRPC,
                          pids=self.hostmap[host])

    def create_process_figs(self, layer, container, rows, cols, label):
        pids = layer.pids()
        for pid in pids:
            title = f'{self.fiter.name} process {pid} {label} latency'
            lfig = LocalFigure(Figure(title, rows, cols))
            container[pid]= lfig

    def process_per_process(self, layer, start, stop,
                            dummy, ypos_cli, ypos_srv):
        if self.per_process and self.client and ypos_cli is not None:
            if not self.client_process:
                self.create_process_figs(layer, self.client_process,
                                         self.NUM_CLI_LAYERS,
                                         self.NUM_COLS, 'client')
            pids = self.client_process.keys()
            for pid in pids:
                lfig = self.client_process[pid]
                self.draw(lfig, ypos_cli,
                          layer, start, stop, layer.layer_type == S3,
                          pids=[pid])

        if self.per_process and self.server and ypos_srv is not None:
            if not self.server_process:
                self.create_process_figs(layer, self.server_process,
                                         self.NUM_SRV_LAYERS,
                                         self.NUM_COLS, 'server')
            pids = self.server_process.keys()
            for pid in pids:
                lfig = self.server_process[pid]
                self.draw(lfig, ypos_srv,
                          layer, start, stop, layer.layer_type == SRPC,
                          pids=[pid])

    def process_layer(self, layer, start, stop,
                      ypos_com, ypos_cli, ypos_srv):
        foos = [self.process_agg, self.process_per_host, self.process_per_process]
        for f in foos:
            f(layer, start, stop, ypos_com, ypos_cli, ypos_srv)

    LAYER_MAP = {
        S3:       {'start': ["START"], 'stop': ["COMPLETE"], 'ypos_com': 0, 'ypos_cli': 0, 'ypos_srv': None},
        MOTR_REQ: {'start': ["initialised"], 'stop': ["stable"], 'ypos_com': 1, 'ypos_cli': 1, 'ypos_srv': None},
        CRPC:     {'start': ["INITIALISED"], 'stop': ["REPLIED"], 'ypos_com': 2, 'ypos_cli': 2, 'ypos_srv': None},
        SRPC:     {'start': ["INITIALISED"], 'stop': ["REPLIED"], 'ypos_com': 3, 'ypos_cli': None, 'ypos_srv': 0},
        FOM:      {'start': ['0','-1'], 'stop': ['finish'], 'ypos_com': 4, 'ypos_cli': None, 'ypos_srv': 1},
        STIO:     {'start': ['M0_AVI_IO_LAUNCH'], 'stop': ['M0_AVI_AD_ENDIO'], 'ypos_com': 5, 'ypos_cli': None, 'ypos_srv': 2},
        BETX:     {'start': ['prepare'], 'stop': ['done'], 'ypos_com': 6, 'ypos_cli': None, 'ypos_srv': 3}
    }

    def consume(self, layer):
        desc = self.LAYER_MAP[layer.layer_type]
        self.process_layer(layer, desc['start'], desc['stop'],
                           desc['ypos_com'], desc['ypos_cli'], desc['ypos_srv'])

    def done(self):
        if self.agg:
            self.cluster_agg.fig.draw()
            self.cluster_agg.fig.save()

            if self.client:
                self.client_agg.fig.draw()
                self.client_agg.fig.save()

            if self.server:
                self.server_agg.fig.draw()
                self.server_agg.fig.save()

        if self.client and self.per_process:
            for pid in self.client_process.keys():
                fig = self.client_process[pid].fig
                fig.draw()
                fig.save()

        if self.server and self.per_process:
            for pid in self.server_process.keys():
                fig = self.server_process[pid].fig
                fig.draw()
                fig.save()

        if self.client and self.per_host:
            for host in self.client_hosts:
                fig = self.client_hosts[host].fig
                fig.draw()
                fig.save()

        if self.server and self.per_host:
            for host in self.server_hosts:
                fig = self.server_hosts[host].fig
                fig.draw()
                fig.save()

        if not self.save_only:
            Figure.show_plt()

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
    s3all = ADD_START_COMPLETE_RGW_REQ_FILTER.run(s3all)
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
    system_rps.py: Generate request per second plots of Cortx S3 and Motr layers
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
    parser.add_argument("--client", action="store_true",
                        help="Show client side of stack: S3, MotrReq, CRPC")
    parser.add_argument("--server", action="store_true",
                        help="Show server side of stack: SRPC, FOM, BETX, STIO")

    parser.add_argument('-a', "--all", action="store_true",
                        help="Plot possible views: cluster-wise, per porcess and per host")
    parser.add_argument("--aggregated", action="store_true",
                        help="Plot cluster-wise (aggregated) view")
    parser.add_argument("--per-host", action="store_true",
                        help="Plot per-host view")
    parser.add_argument("--per-process", action="store_true",
                        help="Plot per-process view")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    pandas_init()

    conn = Connection(args.db)
    conn.connect()

    if not args.s3get and not args.s3put:
        args.s3get = True
        args.s3put = True

    if not args.client and not args.server:
        args.client = True
        args.server = True

    if not args.aggregated and not args.per_process and not args.per_host:
        args.all = True

    if args.all:
        args.aggregated = True
        args.per_process = True
        args.per_host = True

    hostmap = get_hosts_pids(conn)

    if args.s3put:
        handler = Handler(S3PUT_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap,
                          agg=args.aggregated,
                          per_host=args.per_host,
                          per_process=args.per_process,
                          client=args.client,
                          server=args.server)
        calculate(conn, S3PUT_FILTER, handler)

    if args.s3get:
        handler = Handler(S3GET_FILTER, args.avg_window,
                          args.save_only, hostmap=hostmap,
                          agg=args.aggregated,
                          per_host=args.per_host,
                          per_process=args.per_process,
                          client=args.client,
                          server=args.server)
        calculate(conn, S3GET_FILTER, handler)

    return

if __name__ == "__main__":
    main()
