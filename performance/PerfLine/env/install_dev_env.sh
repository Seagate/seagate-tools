#!/bin/bash

set -e

NODES_NUM=
SKIP_K8S=
SKIP_DEPLOYMENT=
SKIP_PERFLINE=

K8S_HOSTS_FILENAME="hosts"
CORTX_RE_DEFAULT_REPO="https://github.com/Seagate/cortx-re"
CORTX_RE_DEFAULT_BRANCH="main"

PERFLINE_DEFAULT_REPO="git@github.com:Seagate/seagate-tools.git"
PERFLINE_DEFAULT_BRANCH="dps"
PERFLINE_HOSTS_FILENAME="seagate-tools/performance/PerfLine/inventories/perfline_hosts/hosts"
PERFLINE_CLIENT_HOST="$(hostname)"

CONFIG_TYPE=automated
SERVICE_FRAMEWORK_SOLUTION="solution.yaml"
SERVICE_FRAMEWORK_DISK=

function usage() {
    cat << HEREDOC
Usage : $0 [--spec input.yaml, --skip-k8s, --skip-deployment, --skip-perfline]
where,
    --spec file - Run script with specified specification file.
                  Default input.yaml is used when not specified.
    --skip-k8s - Skip K8s env installation.
    --skip-deployment - Skip CORTX cluster deployment.
    --skip-perfline - Skip PerfLine installation.
HEREDOC
}

function validate() {
    local cfg_type

    if [ -z "$SPEC_FILE" ] ; then
	SPEC_FILE="input.yaml"
    fi

    if [ ! -f "$SPEC_FILE" ] ; then
	echo "Spec file not found!"
	exit 1
    else
	echo "Using spec file: $SPEC_FILE"
    fi

    NODES_NUM=$(yq_linux_386 '.specification.nodes | length' "$SPEC_FILE")
    if [ "$NODES_NUM" -eq 0 ] ; then
	echo "ERROR: Nodes are not specified"
	exit 1
    else
	echo "Number of nodes: $NODES_NUM"
    fi

    set -x
    cfg_type=$(yq_linux_386 ".specification.config" "$SPEC_FILE")
    if [ "$cfg_type" = "auto" ]   ; then
	CONFIG_TYPE="automated"
    elif [ "$cfg_type" = "manual" ] ; then
	CONFIG_TYPE="manual"
	if [ ! -f "$SERVICE_FRAMEWORK_SOLUTION" ] ; then
	    echo "Missing solution.yaml required for manual configuration"
	fi
    else
	echo "Incorrect option: .specification.config. Shall be \"auto\" or \"manual\""
	exit 1
    fi
    set +x
    
    if [ -z "$SKIP_K8S" ] ; then
	CORTX_RE_REPO=$(yq_linux_386 ".specification.cortx_re.repo" "$SPEC_FILE")
	CORTX_RE_BRANCH=$(yq_linux_386 ".specification.cortx_re.branch" "$SPEC_FILE")
	if [ -z "$CORTX_RE_REPO" -o "$CORTX_RE_REPO" = "null" ] ; then
	    CORTX_RE_REPO="$CORTX_RE_DEFAULT_REPO"
	    echo "Cortx RE repo is not specified, using default: $CORTX_RE_REPO"
	fi

set -x
	if [ -z "$CORTX_RE_BRANCH" -o "$CORTX_RE_BRANCH" = "null" ] ; then
	    CORTX_RE_BRANCH="$CORTX_RE_DEFAULT_BRANCH"
	    echo "Cortx RE branch is not specified, using default: $CORTX_RE_BRANCH"
	fi
set +x
    fi

    if [ -z "$SKIP_DEPLOYMENT" ] ; then
	CORTX_SERVICE_REPO=$(yq_linux_386 ".specification.service_framework.repo" "$SPEC_FILE")
	CORTX_SERVICE_BRANCH=$(yq_linux_386 ".specification.service_framework.branch" "$SPEC_FILE")

	
	if [ -z "$CORTX_SERVICE_REPO" -o "$CORTX_SERVICE_REPO" = "null" ] ; then
	    echo "Cortx Service Framework repo is not specified, using default"
	    CORTX_SERVICE_REPO=
	fi

	if [ -z "$CORTX_SERVICE_BRANCH" -o "$CORTX_SERVICE_BRANCH" = "null" ] ; then
	    echo "Cortx Service Framework branch is not specified, using default"
	    CORTX_SERVICE_BRANCH=
	fi

	SNS_LAYOUT=$(yq_linux_386 ".specification.durability.sns" "$SPEC_FILE")
	if [ $SNS_LAYOUT == "null" ] ; then
	    SNS_LAYOUT=
	fi

	DIX_LAYOUT=$(yq_linux_386 ".specification.durability.dix" "$SPEC_FILE")
	if [ $DIX_LAYOUT == "null" ] ; then
	    DIX_LAYOUT=
	fi

	SERVICE_FRAMEWORK_DISK=$(yq_linux_386 ".specification.service_framework.disk" "$SPEC_FILE")
	if [ "$SERVICE_FRAMEWORK_DISK" = "null" ] ; then
	    SERVICE_FRAMEWORK_DISK=
	fi

	if [ ! -z "$SERVICE_FRAMEWORK_DISK" ] ; then
	    set +e
	    ls /dev/* | grep -q "$SERVICE_FRAMEWORK_DISK"
	    err=$?
	    set -e
	    if [ "$err" -ne "0" ] ; then
		echo "Service Framework disk $SERVICE_FRAMEWORK_DISK is not found"
		exit 1
	    fi
	fi
    fi

    if [ -z "$SKIP_PERFLINE" ] ; then
	PERFLINE_REPO=$(yq_linux_386 ".specification.perfline.repo" "$SPEC_FILE")
	PERFLINE_BRANCH=$(yq_linux_386 ".specification.perfline.branch" "$SPEC_FILE")
	if [ -z "$PERFLINE_REPO" -o "$PERFLINE_REPO" = "null" ] ; then
	    PERFLINE_REPO="$PERFLINE_DEFAULT_REPO"
	    echo "PerfLine repo is not specified, using default: $PERFLINE_REPO"
	fi

	if [ -z "$PERFLINE_BRANCH" -o "$PERFLINE_BRANCH" = "null" ] ; then
	    PERFLINE_BRANCH="$PERFLINE_DEFAULT_BRANCH"
	    echo "PerfLine branch is not specified, using default: $PERFLINE_BRANCH"
	fi

	PERFLINE_CLIENT_HOST=$(yq_linux_386 ".specification.perfline.node" "$SPEC_FILE")
	if [ -z "$PERFLINE_CLIENT_HOST" -o "$PERFLINE_CLIENT_HOST" = "null" ] ; then
	    PERFLINE_CLIENT_HOST=$(hostname)
	fi

	PERFLINE_DISK=$(yq_linux_386 ".specification.perfline.disk" "$SPEC_FILE")
	if [ "$PERFLINE_DISK" = "null" ] ; then
	    PERFLINE_DISK="/dev/sdi"
	fi

	if [ ! -z "$PERFLINE_DISK" ] ; then
	    set +e
	    ls /dev/* | grep -q "$PERFLINE_DISK"
	    err=$?
	    set -e
	    if [ "$err" -ne "0" ] ; then
		echo "PerfLine disk $PERFLINE_DISK is not found"
		exit 1
	    fi
	fi
    fi
}

function check_prereq() {
    # TODO: Check installation type
    # Valid only for auto-installation
    local disks="sdb sdc sdd sde sdf sdg sdh sdi"

    set +e
    error=0
    for disk in $disks; do
	echo -n "Checking presence of disk /dev/$disk: "
	ls /dev/sd* | grep $disk > /dev/null
	if [ "$?" -eq 0  ] ; then
	    echo OK
	else
	    echo FAIL
	    error=1
	fi
    done
    set -e

    if [ "$error" -ne 0 ] ; then
	echo "Disk prerequisites are not met."
	exit 1
    fi
}

function install_deps() {
    if [ ! -f /usr/bin/yq_linux_386 ] ; then
	wget https://github.com/mikefarah/yq/releases/download/v4.24.5/yq_linux_386
	chmod +x yq_linux_386
	cp yq_linux_386 /usr/bin/yq_linux_386
    fi

    # Install deps
    yum install -y pdsh-rcmd-ssh.x86_64
    export PDSH_RCMD_TYPE=ssh
}

function install_k8s() {
    local idx
    local host
    local usr
    local pass
    local is_rocky
    local version_match

    > "$K8S_HOSTS_FILENAME"
    for i in $(seq "$NODES_NUM") ; do
	idx=$((i-1))
	host=$(yq_linux_386 ".specification.nodes[$idx].hostname" "$SPEC_FILE")
	usr=$(yq_linux_386 ".specification.nodes[$idx].username" "$SPEC_FILE")
	pass=$(yq_linux_386 ".specification.nodes[$idx].password" "$SPEC_FILE")
	echo "hostname=${host},user=${usr},pass=${pass}" >> hosts
    done

    rm -rf cortx-re || true
    git clone -b "$CORTX_RE_BRANCH" "$CORTX_RE_REPO"
    cp "$K8S_HOSTS_FILENAME" cortx-re/solutions/kubernetes/hosts

    pushd cortx-re/solutions/kubernetes
    ./cluster-setup.sh true
    popd

    set +e
    cat /etc/os-release | grep "^NAME" | grep -q "Rocky Linux"
    if [ $? -eq 0 ]; then
	is_rocky=true
    fi

    cat /etc/os-release | grep "^VERSION_ID" | grep -q "8.4"
    if [ $? -eq 0 ]; then
	version_match=true
    fi

    if [ "$is_rocky" = true ] && [ "$version_match" = true ] ; then
	echo "Rocky Linux 8.4 detected: Applying network workaround"
	kubectl set env daemonset/calico-node -n kube-system FELIX_IPTABLESBACKEND=NFT
	kubectl set env daemonset/calico-node -n kube-system IP_AUTODETECTION_METHOD=interface=eth3
	sleep 30
	echo "Done"
    fi
    set -e

    echo "K8s framework has been installed successfully!"
}

function deploy_cluster() {
    if [ ! -d cortx-re ] ; then
	echo "Cortx RE repo is missing"
	exit 1
    fi

    if [ -f ~/deploy-scripts/k8_cortx_cloud/deploy-cortx-cloud.sh ] ; then
	set +e
	~/deploy-scripts/k8_cortx_cloud/destroy-cortx-cloud.sh
	set -e
    fi

    if [ "$CONFIG_TYPE" = "manual" ] ; then
	cp $SERVICE_FRAMEWORK_SOLUTION cortx-re/solutions/kubernetes/solution.yaml
    fi

    pushd cortx-re/solutions/kubernetes
    export CORTX_SCRIPTS_REPO="$CORTX_SERVICE_REPO" && export CORTX_SCRIPTS_BRANCH="$CORTX_SERVICE_BRANCH" && export SNS_CONFIG="$SNS_LAYOUT" && export DIX_CONFIG="$DIX_LAYOUT" && export SOLUTION_CONFIG_TYPE="$CONFIG_TYPE" && ./cortx-deploy.sh --cortx-cluster

    ./cortx-deploy.sh --io-sanity

    popd
}

function install_perfline() {
    local host
    local idx
    local client
    local user
    local pass

    yum install -y ansible

    rm -rf seagate-tools || true
    git clone -b "$PERFLINE_BRANCH" "$PERFLINE_REPO"

    sed -i '/^srvnode-/d' "$PERFLINE_HOSTS_FILENAME"
    sed -i '/^client-/d' "$PERFLINE_HOSTS_FILENAME"

    host=$(yq_linux_386 ".specification.nodes[0].hostname" "$SPEC_FILE")
    sed -i "/^\[nodes\]/a srvnode-1 ansible_host=$host" "$PERFLINE_HOSTS_FILENAME"

    for i in $(seq 2 "$NODES_NUM") ; do
	idx=$((i-1))
	host=$(yq_linux_386 ".specification.nodes[$idx].hostname" "$SPEC_FILE")
	sed -i "/^srvnode-$idx/a srvnode-$i ansible_host=$host" "$PERFLINE_HOSTS_FILENAME"
    done

    client=$(yq_linux_386 ".specification.nodes[0].hostname" "$SPEC_FILE")
    sed -i "/^\[client\]/a client-1 ansible_host=$client" "$PERFLINE_HOSTS_FILENAME"

    user=$(yq_linux_386 ".specification.nodes[0].username" "$SPEC_FILE")
    pass=$(yq_linux_386 ".specification.nodes[0].password" "$SPEC_FILE")

    sed -i "s/^ansible_user=.*/ansible_user=$user/g" "$PERFLINE_HOSTS_FILENAME"
    sed -i "s/^cluster_pass=.*/cluster_pass=$pass/g" "$PERFLINE_HOSTS_FILENAME"

    sed -i 's:^disk=.*:disk="/dev/sdb":g' "$PERFLINE_HOSTS_FILENAME"

    mkdir -p /var/perfline
    rm -rf /var/perfline/*
    umount /var/perfline || true
    sed -i "/perfline/d" /etc/fstab

    if [ ! -z "$PERFLINE_DISK" ] ; then
	yes | mkfs.ext4 "$PERFLINE_DISK"
	mount "$PERFLINE_DISK" /var/perfline
	echo "$PERFLINE_DISK /var/perfline ext4 defaults 1 2" >> /etc/fstab
    fi

    pushd seagate-tools/performance/PerfLine
    ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v
    popd
}

function main() {
    install_deps
    validate
    check_prereq

    if [ -z "$SKIP_K8S" ] ; then
	install_k8s
    fi

    if [ -z "$SKIP_DEPLOYMENT" ] ; then
	deploy_cluster
    fi

    if [ -z "$SKIP_PERFLINE" ] ; then
	install_perfline
    fi
}

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--spec)
	    SPEC_FILE=$2
	    shift
	    ;;
        --skip-k8s)
	    SKIP_K8S=true
	    ;;
        --skip-deployment)
	    SKIP_DEPLOYMENT=true
	    ;;
        --skip-perfline)
	    SKIP_PERFLINE=true
	    ;;
        -h|--help)
	    usage
	    exit 0
	    ;;
        *)
            echo -e "Invalid option: $1\nUse --help option"
	    usage
            exit 1
            ;;
    esac
    shift
done

main
