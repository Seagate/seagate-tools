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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpl_patches
from pandas.io import sql
import sqlite3
import gc
import sys
import argparse


from sys_utils import Connection, Layer, Relation, XIDRelation, Histogram, \
                      Figure, S3, MOTR_REQ, COB, CAS, DIX, IOO, CRPC, SRPC, \
                      FOM, STIO, BETX, S3_TO_CLIENT, CLIENT_TO_DIX, \
                      DIX_TO_MDIX, DIX_TO_CAS, CAS_TO_CRPC, CLIENT_TO_COB, \
                      COB_TO_CRPC, CLIENT_TO_IOO, IOO_TO_CRPC, SRPC_TO_FOM, \
                      FOM_TO_STIO, FOM_TO_TX, S3GET_FILTER, S3PUT_FILTER, \
                      ADD_START_COMPLETE_RGW_REQ_FILTER

def pandas_init():
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

def pandas_fini():
    pass


def calculate(conn, fiter, save_only):
    s3fig = Figure(f"{fiter.name} system histograms", 4, 2)
    mfig = Figure(f"{fiter.name} Motr histograms", 6, 3)

    s3all = Layer(S3, conn)
    s3all = ADD_START_COMPLETE_RGW_REQ_FILTER.run(s3all)
    #s3 = S3PUT_FILTER.run(s3all)
    s3 = fiter.run(s3all)

    s3hist = Histogram(s3, ["START"], ["COMPLETE"], bins=50, percentile=0.90)
    s3hist.calculate()
    s3fig.add(s3hist, 0, 0)
    # Cleanup
    del s3all
    gc.collect()

    rel = Relation(S3_TO_CLIENT, conn)
    motr_all = Layer(MOTR_REQ, conn)
    motr = rel.sieve(s3, motr_all)
    motr_hist = Histogram(motr, ["initialised"], ['stable'])
    motr_hist.calculate()
    axs = s3fig.add(motr_hist, 1, 0)
    # Cleanup
    del motr_all
    gc.collect()

    ioo_all = Layer(IOO, conn)
    rel = Relation(CLIENT_TO_IOO, conn)
    ioo = rel.sieve(motr, ioo_all)
    del ioo_all
    gc.collect()
    ioo_hist = Histogram(ioo, ['IO_initial'], ['IO_req_complete'])
    ioo_hist.calculate()
    axm = mfig.add(ioo_hist, 0, 0)

    cob_all = Layer(COB, conn)
    rel = Relation(CLIENT_TO_COB, conn)
    cob = rel.sieve(motr, cob_all)
    del cob_all
    gc.collect()
    cob_hist = Histogram(cob, ['COB_REQ_ACTIVE'], ['COB_REQ_DONE'])
    cob_hist.calculate()
    mfig.add(cob_hist, 0, 1, sharex=axm)

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
    cas_hist = Histogram(cas, ['init'], ['final', 'failure'])
    cas_hist.calculate()
    mfig.add(cas_hist, 0, 2, sharex=axm)

    rpc_all = Layer(CRPC, conn)
    rel_ioo = Relation(IOO_TO_CRPC, conn)
    rel_cob = Relation(COB_TO_CRPC, conn)
    rel_cas = Relation(CAS_TO_CRPC, conn)
    crpc_ioo = rel_ioo.sieve(ioo, rpc_all)
    crpc_cob = rel_cob.sieve(cob, rpc_all)
    crpc_cas = rel_cas.sieve(cas, rpc_all)

    crpc_ioo_hist = Histogram(crpc_ioo, ['INITIALISED'], ['REPLIED'])
    crpc_ioo_hist.calculate()
    mfig.add(crpc_ioo_hist, 1, 0, sharex=axm)

    crpc_cob_hist = Histogram(crpc_cob, ['INITIALISED'], ['REPLIED'])
    crpc_cob_hist.calculate()
    mfig.add(crpc_cob_hist, 1, 1, sharex=axm)

    crpc_cas_hist = Histogram(crpc_cas, ['INITIALISED'], ['REPLIED'])
    crpc_cas_hist.calculate()
    mfig.add(crpc_cas_hist, 1, 2, sharex=axm)

    crpc_hist = Histogram(crpc_ioo, ['INITIALISED'], ['REPLIED'])
    crpc_hist.calculate()
    crpc_hist.merge(crpc_cob_hist)
    crpc_hist.merge(crpc_cas_hist)
    s3fig.add(crpc_hist, 2, 0, sharex=axs)

    del rel_ioo
    del rel_cob
    del rel_cas
    del rpc_all

    rpc_all = Layer(SRPC, conn)
    rel = XIDRelation(conn)
    srpc_ioo = rel.sieve(crpc_ioo, rpc_all)
    srpc_cob = rel.sieve(crpc_cob, rpc_all)
    srpc_cas = rel.sieve(crpc_cas, rpc_all)

    del rpc_all
    del crpc_ioo
    del crpc_cas
    del crpc_cob
    del rel
    gc.collect()

    srpc_ioo_hist = Histogram(srpc_ioo, ['INITIALISED'], ['REPLIED'])
    srpc_ioo_hist.calculate()
    axm = mfig.add(srpc_ioo_hist, 2, 0)

    srpc_cob_hist = Histogram(srpc_cob, ['INITIALISED'], ['REPLIED'])
    srpc_cob_hist.calculate()
    mfig.add(srpc_cob_hist, 2, 1, sharex=axm)

    srpc_cas_hist = Histogram(srpc_cas, ['INITIALISED'], ['REPLIED'])
    srpc_cas_hist.calculate()
    mfig.add(srpc_cas_hist, 2, 2, sharex=axm)

    srpc_hist = Histogram(srpc_ioo, ['INITIALISED'], ['REPLIED'])
    srpc_hist.calculate()
    srpc_hist.merge(srpc_cob_hist)
    srpc_hist.merge(srpc_cas_hist)
    axs = s3fig.add(srpc_hist, 0, 1)

    fom_all = Layer(FOM, conn)
    rel = Relation(SRPC_TO_FOM, conn)
    fom_ioo = rel.sieve(srpc_ioo, fom_all)
    fom_cob = rel.sieve(srpc_cob, fom_all)
    fom_cas = rel.sieve(srpc_cas, fom_all)
    del fom_all
    del rel
    gc.collect()

    fom_ioo_hist = Histogram(fom_ioo, ['0', '-1'], ['finish'])
    fom_ioo_hist.calculate()
    mfig.add(fom_ioo_hist, 3, 0, sharex=axm)

    fom_cob_hist = Histogram(fom_cob, ['0', '-1'], ['finish'])
    fom_cob_hist.calculate()
    mfig.add(fom_cob_hist, 3, 1, sharex=axm)

    fom_cas_hist = Histogram(fom_cas, ['0', '-1'], ['finish'])
    fom_cas_hist.calculate()
    mfig.add(fom_cas_hist, 3, 2, sharex=axm)

    fom_hist = Histogram(fom_ioo, ['0', '-1'], ['finish'])
    fom_hist.calculate()
    fom_hist.merge(fom_cob_hist)
    fom_hist.merge(fom_cas_hist)
    s3fig.add(fom_hist, 1, 1, sharex=axs)

    stio_all = Layer(STIO, conn)
    rel = Relation(FOM_TO_STIO, conn)
    stio_ioo = rel.sieve(fom_ioo, stio_all)
    # stio_cob = rel.sieve(fom_cob, stio_all)        # variable is not being used anywhere
    # stio_cas = rel.sieve(fom_cas, stio_all)        # variable is not being used anywhere
    del stio_all
    del rel
    gc.collect()

    stio_ioo_hist = Histogram(stio_ioo, ['M0_AVI_IO_LAUNCH'], ['M0_AVI_AD_ENDIO'])
    stio_ioo_hist.calculate()
    mfig.add(stio_ioo_hist, 4, 0, sharex=axm)
    s3fig.add(stio_ioo_hist, 2, 1, sharex=axs)

    del stio_ioo
    gc.collect()

    # Only for writes
    if fiter is S3PUT_FILTER:
        betx_all = Layer(BETX, conn)
        rel = Relation(FOM_TO_TX, conn)
        betx_ioo = rel.sieve(fom_ioo, betx_all)
        betx_cob = rel.sieve(fom_cob, betx_all)
        betx_cas = rel.sieve(fom_cas, betx_all)
        del betx_all
        del rel
        gc.collect()

        betx_ioo_hist = Histogram(betx_ioo, ['prepare'], ['done'])
        betx_ioo_hist.calculate()
        mfig.add(betx_ioo_hist, 5, 0, sharex=axm)

        betx_cob_hist = Histogram(betx_cob, ['prepare'], ['done'])
        betx_cob_hist.calculate()
        mfig.add(betx_cob_hist, 5, 1, sharex=axm)

        betx_cas_hist = Histogram(betx_cas, ['prepare'], ['done'])
        betx_cas_hist.calculate()
        mfig.add(betx_cas_hist, 5, 2, sharex=axm)

        betx_hist = Histogram(betx_ioo, ['prepare'], ['done'])
        betx_hist.calculate()
        betx_hist.merge(betx_cob_hist)
        betx_hist.merge(betx_cas_hist)
        s3fig.add(betx_hist, 3, 1, sharex=axs)

    s3fig.draw()
    mfig.draw()

    s3fig.save()
    mfig.save()

    if not save_only:
        s3fig.show()
        mfig.show()

def parse_args():
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="""
    system_hist.py: Generate histograms of Cortx S3 and Motr layers
    """)

    parser.add_argument("-d", "--db", type=str, default="m0play.db",
                        help="Performance database (m0play.db)")
    parser.add_argument("-g",'--s3get', action='store_true', help="Show histograms of S3GetObject operation")
    parser.add_argument("-p", "--s3put", action='store_true', help="Show histograms of S3GetObject operation")
    parser.add_argument("-s", "--save-only", action='store_true', help="Don't show figures, only save")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    pandas_init()

    conn = Connection(args.db)

    if not args.s3get and not args.s3put:
        args.s3get = True
        args.s3put = True

    if args.s3put:
        calculate(conn, S3PUT_FILTER, args.save_only)

    if args.s3get:
        calculate(conn, S3GET_FILTER, args.save_only)

    return

if __name__ == "__main__":
    main()
