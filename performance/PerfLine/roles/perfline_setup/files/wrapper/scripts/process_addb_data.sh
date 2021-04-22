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
    generate_histogram_imgs
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

function generate_histogram_imgs()
{
    echo "generating histograms..."
    python3 $TOOLS_DIR/system_hist.py -s --db $M0PLAY_DB || true
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
