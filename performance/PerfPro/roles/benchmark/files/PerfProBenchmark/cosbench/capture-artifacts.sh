#!/bin/sh
#
# Seagate-tools: PerfPro
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
SHORT=h
LONG=help,controller:,workloadID:,output-directory:

CONTROLLER=""
WORKLOAD_ID=""
OUTPUT_DIR=""

usage() {
  echo 'Usage:'
  echo '  ./capture-artifacts.sh --workloadID <workload ID> --output-directory <local directory to copy output files>'
  echo '      --controller <Controller-IP> [--help]'
}

OPTS=$(getopt --options $SHORT --long $LONG  --name "$0" -- "$@")

eval set -- "$OPTS"

invalid_command() {
  printf "\nInvalid command\n"
  usage
  exit 1
}

while true ; do
  case "$1" in
    --controller )
      CONTROLLER="$2"
      shift 2
      ;;
    -h | --help )
      usage
      exit 0
      ;;
    --workloadID)
      WORKLOAD_ID="$2"
      shift 2
      ;;
    --output-directory )
      OUTPUT_DIR="$2"
      shift 2
      ;;
    -- )
      shift
      break
      ;;
    *)
      printf "$1\n"
      invalid_command
      ;;
  esac
done

if [ "$WORKLOAD_ID" = "" ] || [ "$OUTPUT_DIR" = "" ] || [ "$CONTROLLER" = "" ]
then
  invalid_command
fi

if [ ! -d "$OUTPUT_DIR" ]
then
  mkdir -p "$OUTPUT_DIR"
fi

scp "$(whoami)"@"$CONTROLLER":~/cos/archive/"$WORKLOAD_ID"-\*/"$WORKLOAD_ID"-\*workloadtype.csv  "$OUTPUT_DIR"

