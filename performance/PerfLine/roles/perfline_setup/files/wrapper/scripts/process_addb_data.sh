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

set -e
# set -x

SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
TOOLS_DIR="$SCRIPT_DIR/../../chronometry_v2"

function main()
{
    parse_params "$@"
    check_params
    generate_queue_imgs
    generate_rps_imgs
    generate_latency_imgs
    generate_histogram_imgs
    generate_timeline_imgs
}

function check_params()
{
    if [[ -z "$M0PLAY_DB" ]]; then
        echo "missed required parameter"
        exit 1
    fi

    if [[ ! -f "$M0PLAY_DB" ]]; then
        echo "file $M0PLAY_DB not exists"
        exit 1
    fi
}

function generate_queue_imgs()
{
    echo "generating queues..."
    $TOOLS_DIR/queues.py --db $M0PLAY_DB --no-window --output-file queues_aggr || true
    $TOOLS_DIR/queues.py --db $M0PLAY_DB --no-window -s --output-file queues_srv || true
    $TOOLS_DIR/queues.py --db $M0PLAY_DB --no-window -c --output-file queues_cli || true
}

function generate_rps_imgs()
{
    echo "generating RPS..."
    python3 $TOOLS_DIR/rps.py --db $M0PLAY_DB -w 10ms --s3put --save-only || true
    python3 $TOOLS_DIR/rps.py --db $M0PLAY_DB -w 10ms --s3get --save-only || true
}

function generate_latency_imgs()
{
    echo "generating latency imgs..."
    python3 $TOOLS_DIR/latency.py --db $M0PLAY_DB -w 10ms --s3put --save-only || true
    python3 $TOOLS_DIR/latency.py --db $M0PLAY_DB -w 10ms --s3get --save-only || true
}

function generate_histogram_imgs()
{
    echo "generating histograms..."
    python3 $TOOLS_DIR/system_hist.py -s --db $M0PLAY_DB || true
}

function parse_val()
{
    local param_name="$1"
    local data_str="$2"
    local result=$(echo "$data_str" | grep -E -o "${param_name}:\S+" | sed "s/${param_name}://")
    echo $result
}

function generate_timeline_imgs()
{
    echo "generating timelines..."

    set +e

    $SCRIPT_DIR/req_browser.py --db $M0PLAY_DB | while read line; do
        local fields_nr=$(echo "$line" | awk '{print NF}')
        local workload_part=$(parse_val "time" "$line")
        local req_type=$(parse_val "s3_op" "$line")
        local pid=$(parse_val "s3_pid" "$line")
        local req_id=$(parse_val "s3_reqid" "$line")

        local filename="timeline_${workload_part}_${req_type}_${pid}_${req_id}"

        if [[ "$fields_nr" -gt "4" ]]; then
            local motr_req_pid=$(parse_val "cli_pid" "$line")
            local motr_req_id=$(parse_val "cli_reqid" "$line")

            filename="motr_${filename}_${motr_req_pid}_${motr_req_id}"
            $TOOLS_DIR/req_timelines.py --db $M0PLAY_DB --pid $motr_req_pid --depth 5 --no-window --output-file $filename $motr_req_id
        else
            filename="s3_${filename}"
            $TOOLS_DIR/req_timelines.py --db $M0PLAY_DB --pid $pid --depth 1 --no-window --output-file $filename $req_id
        fi
    done

    set -e
}

parse_params()
{
    while [[ $# -gt 0 ]]; do

        case $1 in
            --db)
                M0PLAY_DB="$2"
                shift
                ;;
            *)
                echo "unsupported parameter: $1"
                exit 1
                ;;
        esac

        shift
    done
}


main "$@"
exit $?
