#!/usr/bin/env python3

import pandas as pd
import os
import sys


def extractFile(filepath):
    files = []
    for r, _, f in os.walk(filepath):
        for file in f:
            if 'loadtype.csv' in file:
                files.append(os.path.join(r, file))
    return files


# def extractData(datafile)
if __name__ == '__main__':
    files = extractFile(sys.argv[1])
    for IO_SIZE in files:
       # print('=============IO_SIZE: {}============='.format(IO_SIZE))
       # print(IO_SIZE)
       # print(pd.read_table(IO_SIZE))
        #print(pd.read_csv(IO_SIZE, header=[4,14], squeeze = True))
        print(pd.read_csv(IO_SIZE, usecols=[
              "Op-Count", "Throughput"], squeeze=True))
