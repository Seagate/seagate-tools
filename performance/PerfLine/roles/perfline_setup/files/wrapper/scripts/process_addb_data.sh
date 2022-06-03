#!/usr/bin/env bash
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

set -e
# set -x

SCRIPT_PATH="$(readlink -f "$0")"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
TOOLS_DIR="$SCRIPT_DIR/../../chronometry"

function main()
{
    parse_params "$@"
    check_params
    #generate_queue_imgs
    generate_rps_imgs
    generate_latency_imgs
    generate_mbps_imgs
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
    "$TOOLS_DIR"/queues.py --db "$M0PLAY_DB" --no-window --output-file queues_aggr || true
    "$TOOLS_DIR"/queues.py --db "$M0PLAY_DB" --no-window -s --output-file queues_srv || true
    "$TOOLS_DIR"/queues.py --db "$M0PLAY_DB" --no-window -c --output-file queues_cli || true
}

function generate_rps_imgs()
{
    echo "generating RPS..."
    python3 "$TOOLS_DIR"/rps.py --db "$M0PLAY_DB" -w 10ms --s3put --save-only || true
    python3 "$TOOLS_DIR"/rps.py --db "$M0PLAY_DB" -w 10ms --s3get --save-only || true
}

function generate_latency_imgs()
{
    echo "generating latency imgs..."
    python3 "$TOOLS_DIR"/latency.py --db "$M0PLAY_DB" -w 10ms --s3put --save-only || true
    python3 "$TOOLS_DIR"/latency.py --db "$M0PLAY_DB" -w 10ms --s3get --save-only || true
}

function generate_mbps_imgs()
{
    echo "generating throughput imgs..."
    python3 "$TOOLS_DIR"/mbps.py --db "$M0PLAY_DB" -w 10ms --s3put --save-only || true
    python3 "$TOOLS_DIR"/mbps.py --db "$M0PLAY_DB" -w 10ms --s3get --save-only || true
}

function generate_histogram_imgs()
{
    echo "generating histograms..."
    python3 "$TOOLS_DIR"/system_hist.py -s --db "$M0PLAY_DB" || true
}

function parse_val()
{
    local param_name="$1"
    local data_str="$2"
    local result=$(echo "$data_str" | grep -E -o "${param_name}:\S+" | sed "s/${param_name}://")
    echo "$result"
}

function generate_timeline_imgs()
{
    echo "generating timelines..."

    set +e

    "$SCRIPT_DIR"/req_browser.py --db "$M0PLAY_DB" | while read line; do
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
            "$TOOLS_DIR"/req_timelines.py --db "$M0PLAY_DB" --pid "$motr_req_pid" --no-window --output-file "$filename" "$motr_req_id"
        else
            filename="s3_${filename}"
            "$TOOLS_DIR"/req_timelines.py --db "$M0PLAY_DB" --pid "$pid" --depth 2 --no-window --output-file "$filename" "$req_id"
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
