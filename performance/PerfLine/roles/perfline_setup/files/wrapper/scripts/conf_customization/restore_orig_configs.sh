#!/bin/bash
set -e
set -x

# This file is a wrapper for specific versions (LR/LC)
# of restore_orig_configs.sh script.
# Please don't put any additional code here. Any required changes
# should be placed in the particular restore_orig_configs.sh LR/LC-version

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../../perfline.conf"

$SCRIPT_DIR/../$CLUSTER_TYPE/conf_customization/restore_orig_configs.sh "$@"

