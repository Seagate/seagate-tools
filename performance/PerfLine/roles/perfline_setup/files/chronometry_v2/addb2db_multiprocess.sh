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
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

declare -A PART_SIZES

function merge_db_parts()
{
    pushd $TMP_DIR
    $SCRIPT_DIR/../wrapper/scripts/merge_m0playdb m0play.db.part.*
    popd
}

function process_parts()
{
    local part_index=$1
    shift

    local db_file="$TMP_DIR/m0play.db.part.${part_index}"
    local dumps_arg=""
    local tmp=""

    for file in $@; do
        local p_size=${PART_SIZES[$file]}
        local start=$(($p_size * $part_index))
        local end=$(($start + $p_size))
        dumps_arg="${dumps_arg}${tmp}[\"$file\",$start,$end]"
        tmp=","
    done

    dumps_arg="[${dumps_arg}]"
    python3 $SCRIPT_DIR/addb2db.py --batch 50 --db $db_file --jdumps $dumps_arg
    echo "processing $part_index finished"
}

function detect_cpu_nr()
{
    CPU_NR=$(lscpu | grep '^CPU(s):' | awk '{print $2}')
    echo "detected $CPU_NR CPUs"
}

function calc_part_sizes()
{
    for file in $@; do
        local l_nr=$(wc -l $file | awk '{print $1}')
        local p_size=$(($l_nr / $CPU_NR))
        p_size=$(($p_size + 1))
        PART_SIZES[$file]="$p_size"
    done
}

function start_working_processes()
{
    local i="0"
    while [[ "$i" -lt "$CPU_NR" ]]; do
        process_parts $i $@ &
        PIDS="$PIDS $!"
        i=$(($i + 1))
    done
}

function wait_for_completion
{
    wait $PIDS
    echo "finished all background processes"
}

function create_temp_dir()
{
    TMP_DIR=$(mktemp -u tmp_addb_XXXXXXX)
    mkdir $TMP_DIR
    echo "tmp dir: $TMP_DIR"
}

function del_temp_dir()
{
    mv ./$TMP_DIR/m0play.db ./
    rm -rf $TMP_DIR
}

function validate_args()
{
    if [[ "$ADDB_DUMPS" == "" ]]; then
        echo "addb dumps is not specified. Please use --help to get more information"
        exit 1
    fi
}

function usage() {
    cat << EOF

Usage: $SCRIPT_NAME [arguments]

Arguments:

    -d, --dumps  List of addb dumps

    -h, --help   This help

Example:
    $SCRIPT_NAME --dumps /path/to/dump1 /path/to/dump2

EOF
}

function parse_args()
{
    while [[ "$#" -ge "1" ]]; do

        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dumps)
                shift
                ADDB_DUMPS="$@"
                return
                ;;
            *)
                echo "unknown argument: $1"
                exit 1
        esac
        shift
    done
}

function main()
{
    parse_args $@
    validate_args
    detect_cpu_nr
    create_temp_dir
    calc_part_sizes $ADDB_DUMPS
    start_working_processes $ADDB_DUMPS
    wait_for_completion
    merge_db_parts
    del_temp_dir
}

main $@
exit $?
