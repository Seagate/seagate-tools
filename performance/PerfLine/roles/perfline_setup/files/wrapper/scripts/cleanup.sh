#!/usr/bin/env bash

set -e
set -x

# This file is a wrapper for specific versions (LR/LC)
# of cleanup.sh script.
# Please don't put any additional code here. Any required changes
# should be placed in the particular cleanup.sh LR/LC-version

SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../perfline.conf"

$SCRIPT_DIR/$CLUSTER_TYPE/cleanup.sh "$@"
