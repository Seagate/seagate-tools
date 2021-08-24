#!/bin/bash
SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"
source "$SCRIPT_DIR/../perfline.conf"
source "$SCRIPT_DIR/.latest_stable_build"

function main() {
    BUILD_LIST=$(curl -s $URL/ | grep href | sed 's/.*href="//' | sed 's/".*//' | grep -o '[[:digit:]]*' | sort -n)
    for build in $BUILD_LIST;
    do
       if (($build>=$BUILDNO))
       then
           BUILD_URLS=("$URL/$build/prod/")
           for workload_file in `ls $WORKLOAD_DIR/*.yaml`
           do  
               sed -i "s/.*priority: .*/  priority: 100/g" $workload_file 
               sed -i "s/.*user: .*/  user: deamon_run@seagate.com/g" $workload_file 
               sed -i "s/.*description:.*/  description: Deamon execution for ${build}/g" $workload_file
               sed -i "s@.*url: .*@  url: ${BUILD_URLS}@g" $workload_file
               $SCRIPT_DIR/perfline.py -a < $workload_file
           done
           echo "BUILDNO=$build" > .latest_stable_build
           echo "Successfully triggered for $build"
       fi
    done
}

function validate() {
    local leave=
    if [[ -z "$URL" ]]; then
       echo "URL is not specified"
       leave="1"
    fi
    
    if [[ -z "$WORKLOAD_DIR" ]]; then
         echo "URL is not specified"
         leave="1"
    fi
   
    if [[ -n $leave ]]; then
        exit 1
    fi
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            URL=$2
            shift
            ;;
        --workload_dir)
            WORKLOAD_DIR=$2
            shift
            ;;
        --help)
            echo -e "Usage: ./perfline_deamon.sh --url 'http://cortx-storage.colo.seagate.com/releases/cortx/github/stable/centos-7.8.2003/' --workload_dir '/root/perfline/wrapper/workload/deamon_runs/'\n"
            exit 0
            ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
            exit 1
            ;;
    esac
    shift
done

validate
main

