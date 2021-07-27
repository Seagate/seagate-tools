#!/usr/bin/env bash
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../perfline.conf"

PL_SCRIPT_PATH=$PERFLINE_DIR/wrapper/perfline.py
PL_DIR="${PL_SCRIPT_PATH%/*}"

pushd $PL_DIR > /dev/null
$PL_SCRIPT_PATH $@
popd > /dev/null
