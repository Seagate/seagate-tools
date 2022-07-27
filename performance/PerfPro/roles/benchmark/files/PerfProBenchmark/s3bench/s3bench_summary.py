#!/usr/bin/env python3
#
# Seagate-tools: PerfPro
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


import os
import sys
from tabulate import tabulate

'''This script takes location of sanity results as argument'''
sanity_results=sys.argv[1]

headers=['Obj_size','Samples','Sessions','Write Tput(MB/s)','Read Tput(MB/s)','Write IOPS','Read IOPS',
         'Write Latency(ms)','Read Latency(ms)','Read TTFB(ms)','Read TTFB(99%)(ms)','Write Errors','Read Errors']

Data=[]

def getallfiles(directory, extension):
    ''' Function to return all file names with perticular extension '''
    flist = []
    for path, _, files in os.walk(directory):
        for name in files:
            if(name.lower().endswith(extension)):
                flist.append(os.path.join(path, name))
    return flist


files = getallfiles(sanity_results, ".log")

def return_results(files):
    '''
    Funtion to return appended list (Data) with values from all the list of files passed as argument
    Input: File list of sanity results.
    Returns: Appended list with summary of results.
    '''
    global Data
    for file in files:
        _, filename = os.path.split(file)
        f = open(file)
        linecount = len(f.readlines())
        f = open(file)
        lines = f.readlines()[-linecount:]
        count = 0
        try:
            while count < linecount:
                if '''"numSamples":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    Objects = int(r[1].replace(",", ""))
                if '''"numClients":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    sessions = int(r[1].replace(",", ""))
                if '''"objectSize(MB)":''' in lines[count].strip().replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    Objsize = float(r[1].replace(",", ""))
                    if(Objsize.is_integer()):
                        obj = str(int(Objsize))+"MB"
                    else:
                        obj = str(round(Objsize*1024))+"KB"

                if '''"Operation":''' in lines[count].replace(" ", ""):
                    r = lines[count].strip().replace(" ", "").split(":")
                    opname = r[1].replace(",", "").strip('"')
                    if opname == "Write":
                        count += 1
                        wrt_tpt=float(lines[count+3].split(":")[1].replace(",", ""))
                        write_iops = round((wrt_tpt/Objsize), 2)
                        write_throughput = round(wrt_tpt, 2)
                        write_errors=int(lines[count-2].split(":")[1].replace(",", ""))
                        write_latency=round(float(lines[count-6].split(":")[1][:-2]),2)
                    elif opname == "Read":
                        count += 1
                        rd_tpt=float(lines[count+3].split(":")[1].replace(",", ""))
                        read_iops = round((rd_tpt/Objsize), 2)
                        read_throughput = round(rd_tpt, 2)
                        read_errors=int(lines[count-2].split(":")[1].replace(",", ""))
                        read_latancy=round(float(lines[count-6].split(":")[1][:-2]),2)
                        read_ttfb=round(float(lines[count+10].split(":")[1][:-2]),2)
                        read_ttfb99p=round(float(lines[count+9].split(":")[1][:-2]),2)
                        file_data=[obj,Objects,sessions,write_throughput,read_throughput,write_iops,
                                  write_latency,read_iops,read_latancy,read_ttfb,read_ttfb99p,write_errors,read_errors]
                        Data.append(file_data)

                        count += 9
                count += 1
        except Exception as e:
            print(f"Encountered error in file: {filename} , and Exeption is", e)
    return(Data)


Data=return_results(files)
print(tabulate(Data,headers=headers,tablefmt='psql'))

