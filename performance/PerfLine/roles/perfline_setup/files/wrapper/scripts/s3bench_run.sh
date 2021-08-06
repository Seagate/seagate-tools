#!/usr/bin/env bash
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

set -x
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../perfline.conf"



function parse_args()
{
    while [[ $# -gt 0 ]]; do
        case $1 in
            -b|--bucket)
                BUCKET_NAME="$2"
                shift
                ;;
            -n|--num-samples)
                NUM_SAMPLES="$2"
                shift
                ;;
            -c|--num-clients)
                NUM_CLIENTS="$2"
                shift
                ;;
            -o|--object-size)
                OBJ_SIZE="$2"
                shift
                ;;
            -f|--dump-file)
                FILE="$2"
                shift
                ;;
            -e|--endpoint)
                ENDPOINT="$2"
                shift
                ;;
            -h|--help)
                echo "help information"
                exit 0
                ;;
            *)
                echo "unknown parameter: $1"
                exit 1
                ;;
        esac
        shift
    done
}


function parse_creds()
{
    if [[ -n "$ACCESS_KEY" && -n "$SECRET_KEY" ]]; then
        return 0
    fi
    ACCESS_KEY=$(egrep ^[^#] ~/.aws/credentials | grep aws_access_key_id | cut -d= -f2 | tr -d " ")
    SECRET_KEY=$(egrep ^[^#] ~/.aws/credentials | grep aws_secret_access_key | cut -d= -f2 | tr -d " ")
}


function run_s3bench()
{
    if [[ -f "s3bench_report.csv" ]]; then
        $PERFLINE_DIR/bin/s3bench_perfline -accessKey $ACCESS_KEY -accessSecret $SECRET_KEY -bucket $BUCKET_NAME -numSamples $NUM_SAMPLES -objectSize $OBJ_SIZE -numClients $NUM_CLIENTS -endpoint "$ENDPOINT" -o s3bench_report.csv -t csv+
    else
        $PERFLINE_DIR/bin/s3bench_perfline -accessKey $ACCESS_KEY -accessSecret $SECRET_KEY -bucket $BUCKET_NAME -numSamples $NUM_SAMPLES -objectSize $OBJ_SIZE -numClients $NUM_CLIENTS -endpoint "$ENDPOINT" -o s3bench_report.csv -t csv
    fi

    
}

parse_args $@
parse_creds
run_s3bench
