#!/bin/bash

set -e
set -x

SCRIPT_NAME=`echo $0 | awk -F "/" '{print $NF}'`
SCRIPT_PATH="$(readlink -f $0)"
SCRIPT_DIR="${SCRIPT_PATH%/*}"

PERFLINE_DIR="$SCRIPT_DIR/../.."
DOCKER_DIR="$PERFLINE_DIR/docker"
CORTX_DIR="$DOCKER_DIR/cortx"
RPM_DIR="$PERFLINE_DIR/rpm"

DOCKER_ARTIFACTS_DIR="/var/artifacts"
BUILD_DIR="$DOCKER_ARTIFACTS_DIR/0"

source "$SCRIPT_DIR/../../perfline.conf"
source "$SCRIPT_DIR/cluster_status.sh"

EX_SRV="pdsh -S -w $NODES"
PRIMARY_NODE=$(echo "$NODES" | cut -d "," -f1)

MOTR_BRANCH=
S3_BRANCH=
HARE_BRANCH=
UTILS_BRANCH=
URL=

function prepare_env() {
    local docker_installed=
    local status=
    
    set +e
    yum list installed | grep docker
    docker_installed=$?
    set -e

    if [ $docker_installed -ne 0 ]; then
	yum install -y docker
    fi

    set +e
    systemctl status docker
    status=$?
    set -e

    if [ $status -ne 0 ]; then
	systemctl restart docker
	systemctl enable docker
    fi

    set +e
    systemctl status docker
    status=$?
    set -e

    if [ $status -ne 0 ]; then
	echo "Docker failure, exit"
	exit 1
    fi

    if [ ! -d "$CORTX_DIR" ]; then
	mkdir -p $DOCKER_DIR
	pushd $DOCKER_DIR
	git clone --recursive https://github.com/Seagate/cortx
	popd
    fi
}

function check_version() {

    # NOTE: currently Motr can be built with either Lnet or Libfabric.
    # There is no way to check if installed version of Motr was built
    # with Lnet or Libfabric.
    # `m0d --version` doesn't contain any mention about it.
    # Name of Cortx-Motr RPM package doesn't have it either.
    # Since we are not able to check if current installed version of Motr
    # is the same what we want to have we need always to upgrade Motr.
    # Details can be found in the ticket https://jts.seagate.com/browse/EOS-25356

    # If branch name is passed, find theirs commit id
    # motr_ver=`git ls-remote $MOTR_REPO $MOTR_BRANCH | cut -f1 | cut -c1-8`
    s3_ver=`git ls-remote $S3_REPO $S3_BRANCH | cut -f1 | cut -c1-8` 
    # hare_ver=`git ls-remote $HARE_REPO $HARE_BRANCH | cut -f1 | cut -c1-8`

    # if [ -n "${motr_ver}" ]; then
	# is_motr_same=`yum list installed | grep cortx-motr | grep ${motr_ver}` || true
    # fi

    if [ -n "${s3_ver}" ]; then
	is_s3_same=`yum list installed | grep cortx-s3server | grep ${s3_ver}` || true
    fi

    # if [ -n "${hare_ver}" ]; then
	# is_hare_same=`yum list installed | grep cortx-hare | grep ${hare_ver}` || true
    # fi

    if [ -n "${UTILS_REPO}" ]; then
	utils_ver=`git ls-remote $UTILS_REPO $UTILS_BRANCH | cut -f1 | cut -c1-8`

	if [ -n "${utils_ver}" ]; then
	    is_utils_same=`yum list installed | grep cortx-py | grep ${utils_ver}` || true
	fi
    else
	is_utils_same="yes"
    fi
    
    # if [ -n "${is_motr_same}" -a -n "${is_s3_same}" -a -n "${is_hare_same}" -a -n "${is_utils_same}" ]; then
	# echo "Requested versions already installed"
	# exit 0
    # fi

    # Otherwise branches may be passed as commit_ids. 
    # In this case `git ls-remote` gives empty string.
    # motr_ver=`echo $MOTR_BRANCH | cut -c1-8`
    s3_ver=`echo $S3_BRANCH | cut -c1-8`
    # hare_ver=`echo $HARE_BRANCH | cut -c1-8`
    utils_ver=`echo $UTILS_BRANCH | cut -c1-8`
    
    # if [ -z "${is_motr_same}" ]; then
	# is_motr_same=`yum list installed | grep cortx-motr | grep ${motr_ver}` || true
    # fi

    if [ -z "${is_s3_same}" ]; then
	is_s3_same=`yum list installed | grep cortx-s3server | grep ${s3_ver}` || true
    fi

    # if [ -z "${is_hare_same}" ]; then
	# is_hare_same=`yum list installed | grep cortx-hare | grep ${hare_ver}` || true
    # fi

    if [ -z "${is_utils_same}" ]; then
	is_utils_same=`yum list installed | grep cortx-py | grep ${utils_ver}` || true
    fi
    
    # if [ -n "${is_motr_same}" -a -n "${is_s3_same}" -a -n "${is_hare_same}" -a -n "${is_utils_same}" ]; then
	# echo "Requested versions already installed"
	# exit 0
    # fi
}

function checkout() {
    if [ -n "${MOTR_BRANCH}" -a -n "${MOTR_REPO}" ]; then
        cd $CORTX_DIR
        rm -rf ./cortx-motr || true
        git clone --recursive $MOTR_REPO cortx-motr
        cd $CORTX_DIR/cortx-motr
        git fetch --all
        git checkout $MOTR_BRANCH

        if [ -n "$BUILD_MOTR_WITH_LNET" ]; then
            echo "Motr will be built with Lnet"
            sed -i '/libfabric/d' cortx-motr.spec.in
        fi
    fi

    if [ -n "${S3_BRANCH}" -a -n "${S3_REPO}" ]; then
	cd $CORTX_DIR
	rm -rf ./cortx-s3server || true
	git clone --recursive $S3_REPO cortx-s3server
	cd $CORTX_DIR/cortx-s3server
	git fetch --all
	git checkout $S3_BRANCH
    fi

    if [ -n "${HARE_BRANCH}" -a -n "${HARE_REPO}" ]; then
	cd $CORTX_DIR
	rm -rf ./cortx-hare || true
	git clone --recursive $HARE_REPO cortx-hare
	cd $CORTX_DIR/cortx-hare
	git fetch --all
	git checkout $HARE_BRANCH
    fi

    if [ -n "${UTILS_BRANCH}" -a -n "${UTILS_REPO}" ]; then
	cd $CORTX_DIR
	rm -rf ./cortx-utils || true
	git clone --recursive $UTILS_REPO cortx-utils
	cd $CORTX_DIR/cortx-utils
	git fetch --all
	git checkout $UTILS_BRANCH
    fi
}

function build() {
    mkdir -p $BUILD_DIR/cortx_iso
    
    cd $CORTX_DIR/..

    # time docker run --rm -v $DOCKER_ARTIFACTS_DIR:$DOCKER_ARTIFACTS_DIR -v ${CORTX_DIR}:/cortx-workspace ghcr.io/seagate/cortx-build:centos-7.8.2003 make clean build -i
    
    time docker run --rm -v $DOCKER_ARTIFACTS_DIR:$DOCKER_ARTIFACTS_DIR -v ${CORTX_DIR}:/cortx-workspace ghcr.io/seagate/cortx-build:centos-7.9.2009 make clean build -i

    pushd $BUILD_DIR
    popd
}

function copy() {
    # Copy RPMs
    pdsh -S -w $NODES "rm -rf -- $RPM_DIR/update"
    pdsh -S -w $NODES "mkdir -p $RPM_DIR/update"

    for srv in $(echo $NODES | tr ',' ' '); do
	scp -r $BUILD_DIR/* $srv:$RPM_DIR/update &
    done
    wait
}

function download() {
    pdsh -S -w $NODES "rm -rf -- $RPM_DIR/update"
    pdsh -S -w $NODES "mkdir -p $RPM_DIR/update/cortx_iso/"

    for file in $(curl -s $URL/cortx_iso/ | grep href | sed 's/.*href="//' | sed 's/".*//' | grep '^[a-zA-Z].*' | grep 'rpm')
    do
        pdsh -S -w $NODES "cd $RPM_DIR/update/cortx_iso/; curl -s -O $URL/cortx_iso/$file"
    done
}

function stop_cluster() {
    if [ "$HA_TYPE" == "pcs" ]; then
         pdsh -S -w $NODES 'systemctl status haproxy' | grep Active
         set +e
         ssh $PRIMARY_NODE 'hctl status'
         if [ $? -eq 0 ]; then
            ssh $PRIMARY_NODE 'cortx cluster stop --all'
         fi
         set -e
    else
         ssh $PRIMARY_NODE 'hctl shutdown || true'
    fi
}

function backup_configs() {
    local time=`date +"%Y_%m_%d_%I_%M_%p"`
    local cfg_backup_dir="$PERFLINE_DIR/config_backup/$time"
    pdsh -S -w $NODES "mkdir -p $cfg_backup_dir"
    pdsh -S -w $NODES "cp /etc/sysconfig/motr $cfg_backup_dir/motr"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/s3/conf/s3config.yaml $cfg_backup_dir/s3config.yaml"
    pdsh -S -w $NODES "cp /etc/haproxy/haproxy.cfg $cfg_backup_dir/haproxy.cfg"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/s3/s3startsystem.sh $cfg_backup_dir/s3startsystem.sh"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/s3/s3backgrounddelete/config.yaml $cfg_backup_dir/config.yaml"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/s3/s3backgrounddelete/s3_cluster.yaml $cfg_backup_dir/s3_cluster.yaml"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/auth/resources/authserver.properties $cfg_backup_dir/authserver.properties"
    pdsh -S -w $NODES "cp /opt/seagate/cortx/auth/resources/keystore.properties $cfg_backup_dir/keystore.properties"
 
    pdsh -S -w $NODES "ls -lsah $cfg_backup_dir"
}

function update() {
    local motr_exist=
    local hare_exist=
    local s3_exist=
    local utils_exis=

    set +e
    pdsh -S -w $NODES "ls -1 $RPM_DIR/update/cortx_iso/ | grep cortx-motr-2"
    motr_exist=$?
    pdsh -S -w $NODES "ls -1 $RPM_DIR/update/cortx_iso/ | grep cortx-hare-2"
    hare_exist=$?
    pdsh -S -w $NODES "ls -1 $RPM_DIR/update/cortx_iso/ | grep cortx-s3server-2"
    s3_exist=$?
    pdsh -S -w $NODES "ls -1 $RPM_DIR/update/cortx_iso/ | grep cortx-py-utils-2"
    utils_exist=$?
    set -e

    if [ ${motr_exist} -ne 0 -o ${hare_exist} -ne 0 -o ${s3_exist} -ne 0 -o ${utils_exist} -ne 0 ]; then
	echo "Packages not found"
	exit 1
    fi
    
    backup_configs

    if [ -n "$BUILD_MOTR_WITH_LNET" ]; then
        # Motr services can't start in case if Motr built without
        # libfabric and libfabric.rpm is installed on the cluster nodes.
        # details can be found at https://jts.seagate.com/browse/EOS-25356
        echo "trying to remove libfabric RPM"
        pdsh -S -w $NODES "yum erase -y libfabric"
    else
        pdsh -S -w $NODES "yum install -y libfabric"
    fi

    if [ -z "${is_hare_same}" -o -z "${is_motr_same}" ]; then
        set +e
        pdsh -S -w $NODES "rpm -Uvh --oldpackage --nodeps --force $RPM_DIR/update/cortx_iso/cortx-motr-2* $RPM_DIR/update/cortx_iso/cortx-hare-2*"
        status=$?
        set -e

        if [ ${status} -ne 0 ]; then
            echo "Cortx-motr and cortx-hare installation failed"
            exit 1
        fi
    fi

    if [ -z "${is_s3_same}" ]; then

        # 'preupgrade' step needs to be done before s3 RPM upgrade.
        # Details can be found at
        # https://github.com/Seagate/cortx-s3server/wiki/S3server-provisioning-on-single-node-VM-cluster:-Manual#optional-pre-upgrade-and-post-upgrade-steps
        pdsh -S -w $NODES "/opt/seagate/cortx/s3/bin/s3_setup preupgrade"
        set +e
        pdsh -S -w $NODES "rpm -Uvh --oldpackage --nodeps --force $RPM_DIR/update/cortx_iso/cortx-s3server-2*"
        status=$?
        set -e
        pdsh -S -w $NODES "/opt/seagate/cortx/s3/bin/s3_setup postupgrade"

        if [ ${status} -ne 0 ]; then
            echo "Cortx-s3server installation failed"
            exit 1
        fi
    fi
	
    # Handle cortx-py-utils also -- if passed by URL update ALWAYS
    # For branches - deploy cortx-py-utils only if is requisted
    if [ -n "${UTILS_BRANCH}" -a -z "${is_utils_same}" ]; then
        set +e
        pdsh -S -w $NODES "rpm -Uvh --oldpackage --nodeps --force $RPM_DIR/update/cortx_iso/cortx-py-utils-2*"
        status=$?
        set -e

        if [ ${status} -ne 0 ]; then
            echo "Cortx-utils installation failed"
            exit 1
        fi
    fi
}

function stop_services() {
    pdsh -S -w $NODES "systemctl stop slapd || true"
    pdsh -S -w $NODES "systemctl stop s3authserver || true"
    pdsh -S -w $NODES "systemctl stop haproxy || true"
}

function check_cluster_status() {
    local wait_period=0
    while ! is_cluster_online $PRIMARY_NODE
    do
       wait_period=$(($wait_period+10))
       if [ $wait_period -gt 600 ];then
          break
       else
          sleep 10
       fi

    done   
}

function pcs_cluster_start() {
    pdsh -S -w $NODES "systemctl start haproxy || true"
    ssh $PRIMARY_NODE '/opt/seagate/cortx/s3/bin/s3_setup post_install --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    ssh $PRIMARY_NODE '/opt/seagate/cortx/s3/bin/s3_setup prepare --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    ssh $PRIMARY_NODE '/opt/seagate/cortx/s3/bin/s3_setup config --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    ssh $PRIMARY_NODE '/opt/seagate/cortx/s3/bin/s3_setup init --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    ssh $PRIMARY_NODE '/opt/seagate/cortx/motr/bin/motr_setup config --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    ssh $PRIMARY_NODE '/opt/seagate/cortx/hare/bin/hare_setup init --config "json:///opt/seagate/cortx_configs/provisioner_cluster.json"'
    pdsh -S -w $NODES "systemctl start haproxy || true"
    ssh $PRIMARY_NODE 'cortx cluster start'
  
 }

 function pcs_cluster_reinit() {
    NUM_PCS_BOOTSTRAP_ATTEMPTS=3
    for i in {1..$NUM_PCS_BOOTSTRAP_ATTEMPTS}; 
    do
       pdsh -S -w $NODES "systemctl status haproxy" | grep Active
       if is_cluster_online $PRIMARY_NODE; then
          ssh $PRIMARY_NODE 'cortx cluster stop --all'
       fi
       pcs_cluster_start
       check_cluster_status
       if is_cluster_online $PRIMARY_NODE; then
          create_s3Account
          break
       fi       
    done
}

function create_s3Account() {
    ssh $PRIMARY_NODE "$PERFLINE_DIR/s3account/create_user.sh"
    ssh $PRIMARY_NODE "$PERFLINE_DIR/s3account/setup_aws.sh"
    ssh $PRIMARY_NODE "cat /root/.aws/credentials" > /root/.aws/credentials
}

function start_services() {
    pdsh -S -w $NODES "systemctl start haproxy || true"
    pdsh -S -w $NODES "systemctl start slapd || true"
    pdsh -S -w $NODES "systemctl start s3authserver || true"

    set +e
    if [[ "$HA_TYPE" == "pcs" ]]; then
        pcs_cluster_start
        check_cluster_status   
        if ! is_cluster_online $PRIMARY_NODE; then
            pcs_cluster_reinit
        else
            create_s3Account
        fi
    fi

    # Check status of s3authserver
    pdsh -S -w $NODES "systemctl status s3authserver"
    status=$?
    set -e

    if [ ${status} -ne 0 ]; then
	echo "S3authserver failed"
	exit 1
    fi
    
}

function main() {
    echo $@
    prepare_env
    check_version

    if [[ -n "$URL" ]]; then
         download
    else
         checkout
         build
         copy
    fi

    stop_cluster
    stop_services
    update
    start_services
}

function validate() {
    local leave=

    if [[ -z "$URL" ]]; then
       if [[ -z "$MOTR_BRANCH" ]]; then
           echo "Motr branch is not specified"
           leave="1"
       fi
   
       if [[ -z "$S3_BRANCH" ]]; then
           echo "S3 server branch is not specified"
           leave="1"
       fi
   
       if [[ -z "$HARE_BRANCH" ]]; then
           echo "Hare branch is not specified"
           leave="1"
       fi
    fi

    if [[ -n $leave ]]; then
        exit 1
    fi
}

function check_arg_count() {
    [[ $# -gt 2 ]] || {
        echo -e "Incorrect use of the option $1\nUse --help option"
        exit 1
    }
}

echo "parameters: $@"

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--motr_id)
	    check_arg_count $1 $2 $3
	    MOTR_REPO=$2
            MOTR_BRANCH=$3
            shift
            shift
            ;;
        -h|--hare_id)
	    check_arg_count $1 $2 $3
	    HARE_REPO=$2
            HARE_BRANCH=$3
            shift
            shift
            ;;
    --use-lnet)
        BUILD_MOTR_WITH_LNET='1'
        ;;
	-s|--s3_id)
	    check_arg_count $1 $2 $3
            S3_REPO=$2
            S3_BRANCH=$3
            shift
	    shift
            ;;
	-u|--utils_id)
	    check_arg_count $1 $2 $3
            UTILS_REPO=$2
            UTILS_BRANCH=$3
            shift
	    shift
            ;;
	--nodes)
            NODES=$2
            EX_SRV="pdsh -S -w $NODES"
            shift
            ;;
	--url)
            URL=$2
            shift
            ;;
	--help)
	    echo -e "Usage: bash update.sh --motr_id a1b2d3e --s3_id bbccdde --hare_id abcdef1\n" 
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
