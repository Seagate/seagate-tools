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
LONG=help,controller:,list_running,cancel:
CONTROLLER=""
USERNAME="$(whoami)"

usage() {
  echo 'Usage:'
  echo '  ./manage-workload-status.sh --list_running | --cancel <workload id>'
  echo '       --controller <controller-ip> [--help]'
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
    --list_running )
      if [ "$ACTION" == "--cancel" ]
      then
        invalid_command
      fi
      ACTION="$1"
      shift 1
      ;;
    --cancel )
      if [ "$ACTION" == "--list_running" ]
      then
         invalid_command
      fi
      ACTION="$1"
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

if [ "$ACTION" == "--list_running" ]
then
  result=$(ssh "$USERNAME"@"$CONTROLLER" "cd ~/cos; sh cli.sh info")
  echo "$result"
fi

if [ "$ACTION" == "--cancel" ]
then
  result=$(ssh "$USERNAME"@"$CONTROLLER" "cd ~/cos; sh cli.sh cancel \$WORKLOAD_ID")
  echo "$result"
fi
