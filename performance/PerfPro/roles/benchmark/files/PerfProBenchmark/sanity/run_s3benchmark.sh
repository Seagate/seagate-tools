#! /usr/bin/bash
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

TOOL_NAME='s3bench'
ACCESS_KEY=$(grep -A 3 default /root/.aws/credentials | grep aws_access_key_id | cut -d " " -f3)
SECRET_KEY=$(grep -A 3 default /root/.aws/credentials | grep secret_access_key | cut -d " " -f3)
BINPATH=/root/PerfProBenchmark/s3bench
CURRENTPATH=$(pwd)
BENCHMARKLOG=$CURRENTPATH/benchmark.log
#ENDPOINTS=https://s3.seagate.com         
BUCKETNAME="seagate"
CLIENTS=""     
NUMSAMPLES=""     
IO_SIZE=""
CONFIG="/root/PerfProBenchmark/config.yml"
ENDPOINTS=$(python3 /root/PerfProBenchmark/get_param.py $CONFIG)         
#RESULT_DIR=/root/PerfProBenchmark/perfpro_build$BUILD/results
RESULT_DIR=/root/PerfProBenchmark/sanity_results/
REGION=us-east-1

validate_args() {

        if [[ -z $CLIENTS ]] || [[ -z $NUMSAMPLES ]] || [[ -z $IO_SIZE ]] ; then
                show_usage
        fi

}

show_usage() {
        echo -e "\n \t  Usage : ./run_s3benchmark.sh -nc NO_OF_CLIENTS -ns NO_OF_SAMPLES -s \"iosize\"   \n"
        echo -e "\t -nc\t:\t number of clients \n"
        echo -e "\t -ns\t:\t number of samples\n"
        echo -e "\t -s\t:\t size of the objects in bytes\n"       
        echo -e "\tExample\t:\t ./run_s3benchmark.sh -nc 128,256,512 -ns 1024,2048,4096 -s 4Kb,16Kb,1Mb,4Mb,128Mb  \n"
        exit 1
}


s3benchmark() {
for NO_OF_SAMPLES in ${NUMSAMPLES//,/ }     
do
    for NUMCLIENTS in ${CLIENTS//,/ }
    do 
        for SIZE_OF_OBJECTS in  ${IO_SIZE//,/ }    
        do
            bucket=$BUCKETNAME-$RANDOM
            aws s3 mb s3://$bucket
            value=$(echo "$SIZE_OF_OBJECTS" | sed -e 's/Kb//g' | sed -e 's/Mb//g' )
            units=$(echo "${SIZE_OF_OBJECTS:(-2)}")
            case "$units" in
                 Mb)   let 'value *= 1024 * 1024'  ;;
                 Kb)   let 'value *= 1024' ;;
              #  b|'')   let 'value += 0'    ;;
                 *)
                     echo "Unsupported units '$units'" >&2
                 ;;
            esac

            echo "S3Benchmark is running for object size : $SIZE_OF_OBJECTS, Clients: $NUMCLIENTS"
            
            echo 'y' | rm report.s3bench > /dev/null 2>&1
            rm -rf s3bench-*.log

            TOOL_DIR=$BENCHMARKLOG/$TOOL_NAME/numclients_$NUMCLIENTS/buckets_1/$SIZE_OF_OBJECTS
            mkdir -p "$TOOL_DIR"
 
#            if [ $SIZE_OF_OBJECTS = "1Kb" ]; then         
#                  echo "$BINPATH/s3bench_perfpro -region $REGION -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -headObj -putObjTag -getObjTag" 

#                  $BINPATH/s3bench_perfpro -region $REGION -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS -headObj -putObjTag -getObjTag -o $TOOL_DIR/report.s3bench -label object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS

#                  mv s3bench-object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS.log $TOOL_DIR/s3bench_object_$SIZE_OF_OBJECTS\_numsamples_$NO_OF_SAMPLES\_buckets_1\_sessions_$NUMCLIENTS\.log
   
#            else 
            echo "$BINPATH/s3bench_perfpro -region $REGION -accessKey=$ACCESS_KEY  -accessSecret=$SECRET_KEY -bucket=$bucket -endpoint=$ENDPOINTS -numClients=$NUMCLIENTS -numSamples=$NO_OF_SAMPLES -objectNamePrefix=loadgen -objectSize=$SIZE_OF_OBJECTS"

            "$BINPATH"/s3bench_perfpro -region="$REGION" -accessKey="$ACCESS_KEY"  -accessSecret="$SECRET_KEY" -bucket="$bucket" -endpoint="$ENDPOINTS" -numClients="$NUMCLIENTS" -numSamples="$NO_OF_SAMPLES" -objectNamePrefix=loadgen -objectSize="$SIZE_OF_OBJECTS" -skipCleanup -o "$TOOL_DIR"/report.s3bench -label object_"$SIZE_OF_OBJECTS"\_numsamples_"$NO_OF_SAMPLES"\_buckets_1\_sessions_"$NUMCLIENTS"

                  mv s3bench-object_"$SIZE_OF_OBJECTS"\_numsamples_"$NO_OF_SAMPLES"\_buckets_1\_sessions_"$NUMCLIENTS".log "$TOOL_DIR"/sanity_s3bench_object_"$SIZE_OF_OBJECTS"\_numsamples_"$NO_OF_SAMPLES"\_buckets_1\_sessions_"$NUMCLIENTS"\.log

            #fi
            echo "S3Benchmark is completed for object size : $SIZE_OF_OBJECTS"
	    sleep 1
        done
        echo "S3Benchmark is completed for number of clients : $NUMCLIENTS"
    done
    echo "S3Benchmark is completed for number of Samples : $NO_OF_SAMPLES"
done
echo 'Successfully completed'

}

while [ ! -z "$1" ]; do
        
        case $1 in
        -nc)     shift
                CLIENTS="$1"
        ;;

        -ns)    shift
                NUMSAMPLES="$1"
        ;;

        -s)    shift
                IO_SIZE="$1"       
        ;;
        
        *)     
                show_usage
                break
        esac
        shift
done

validate_args

if [ ! -d "$BENCHMARKLOG" ]; then
     mkdir "$BENCHMARKLOG"
     s3benchmark
     cp -r "$BENCHMARKLOG"/"$TOOL_NAME" "$RESULT_DIR"/

else
     rm -rf "$BENCHMARKLOG"
     mkdir "$BENCHMARKLOG"
     s3benchmark
     cp -r "$BENCHMARKLOG"/"$TOOL_NAME" "$RESULT_DIR"/     

fi
