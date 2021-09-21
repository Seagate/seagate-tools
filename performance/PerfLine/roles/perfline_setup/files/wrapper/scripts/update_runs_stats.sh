#!/bin/bash 

set -x
set -e

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../../perfline.conf"

echo "Will update statistics for $1 runs"

BUILD_TYPE=$1

mkdir -p $NIGHT_ARTIFACTS/$BUILD_TYPE/img
mkdir -p $NIGHT_ARTIFACTS/$BUILD_TYPE/data
mkdir -p $NIGHT_ARTIFACTS/$BUILD_TYPE/table

list=""
for d in $ARTIFACTS_DIR/result*; do
    if [ -f $d/perfline_metadata.json ]; then
	set +e
	cat $d/perfline_metadata.json | grep "Daemon" | grep $BUILD_TYPE
	ret=$?
	set -e
	if [ $ret -eq 0 ]; then
	    list+="$d "
	fi
    fi
done

pushd $SCRIPT_DIR
python3 fetch.py $BUILD_TYPE "$list"
popd
