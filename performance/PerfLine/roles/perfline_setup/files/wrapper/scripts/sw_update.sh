#!/bin/bash
set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../perfline.conf"

$SCRIPT_DIR/$CLUSTER_TYPE/update.sh "$@"
