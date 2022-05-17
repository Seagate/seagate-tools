#!/bin/bash

set -e
# set -x

SPEC_FILE="$1"

if [ -z "${SPEC_FILE}" ]; then
    echo "ERROR: No specification provided"
    exit 1
fi

DISKS="sdb sdc sdd sde sdf sdg sdh sdi"

set +e
error=0
for disk in $DISKS; do
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
    echo "Disk prerequisites are not met"
fi

wget https://github.com/mikefarah/yq/releases/download/v4.24.5/yq_linux_386
chmod +x yq_linux_386
cp yq_linux_386 /usr/bin/yq_linux_386

> hosts
nodes_num=$(yq_linux_386 '.specification.nodes | length' ${SPEC_FILE})
if [ "$nodes_num" -eq 0 ] ; then
    echo "ERROR: Nodes are not specified"
    exit 1
fi

for i in $(seq $nodes_num) ; do
    idx=$((i-1))
    host=$(yq_linux_386 ".specification.nodes[$idx].hostname" ${SPEC_FILE})
    usr=$(yq_linux_386 ".specification.nodes[$idx].username" ${SPEC_FILE})
    pass=$(yq_linux_386 ".specification.nodes[$idx].password" ${SPEC_FILE})
    echo "hostname=${host},user=${usr},pass=${pass}" >> hosts
done

# Install deps
yum install -y pdsh-rcmd-ssh.x86_64
export PDSH_RCMD_TYPE=ssh

# Cortx-RE
echo "Cortx RE"
repo=$(yq_linux_386 ".specification.cortx_re.repo" ${SPEC_FILE})
branch=$(yq_linux_386 ".specification.cortx_re.branch" ${SPEC_FILE})

rm -rf cortx-re || true
git clone -b $branch $repo

cp hosts cortx-re/solutions/kubernetes/hosts
pushd cortx-re/solutions/kubernetes

./cluster-setup.sh true

kubectl set env daemonset/calico-node -n kube-system FELIX_IPTABLESBACKEND=NFT
kubectl set env daemonset/calico-node -n kube-system IP_AUTODETECTION_METHOD=interface=eth3

sleep 30

# TODO: Currently automated build is used. Use manual and patch solution.example.yaml
export CORTX_SCRIPTS_BRANCH="v0.5.0" && export SOLUTION_CONFIG_TYPE=automated && ./cortx-deploy.sh --cortx-cluster

./cortx-deploy.sh --io-sanity

popd 

repo=$(yq_linux_386 ".specification.perfline.repo" ${SPEC_FILE})
branch=$(yq_linux_386 ".specification.perfline.branch" ${SPEC_FILE})

yum install -y ansible

rm -rf seagate-tools || true
git clone -b $branch $repo

PL_HOSTS="seagate-tools/performance/PerfLine/inventories/perfline_hosts/hosts"

sed -i '/^srvnode-/d' ${PL_HOSTS}
sed -i '/^client-/d' ${PL_HOSTS}

host=$(yq_linux_386 ".specification.nodes[0].hostname" ${SPEC_FILE})
sed -i "/^\[nodes\]/a srvnode-1 ansible_host=$host" ${PL_HOSTS}
echo $nodes_num
for i in $(seq 2 $nodes_num) ; do
    idx=$((i-1))
    host=$(yq_linux_386 ".specification.nodes[$idx].hostname" ${SPEC_FILE})
    sed -i "/^srvnode-$idx/a srvnode-$i ansible_host=$host" ${PL_HOSTS}
done

client=$(yq_linux_386 ".specification.nodes[0].hostname" ${SPEC_FILE})
sed -i "/^\[client\]/a client-1 ansible_host=$client" ${PL_HOSTS}

user=$(yq_linux_386 ".specification.nodes[0].username" ${SPEC_FILE})
pass=$(yq_linux_386 ".specification.nodes[0].password" ${SPEC_FILE})

sed -i "s/^ansible_user=.*/ansible_user=$user/g" $PL_HOSTS
sed -i "s/^cluster_pass=.*/cluster_pass=$pass/g" $PL_HOSTS

sed -i 's:^disk=.*:disk="/dev/sdb":g' $PL_HOSTS

mkdir -p /var/perfline
rm -rf /var/perfline/*
umount /var/perfline || true
yes | mkfs.ext4 /dev/sdi
mount /dev/sdi /var/perfline
sed -i "/perfline/d" /etc/fstab
echo "/dev/sdi /var/perfline ext4 defaults 1 2" >> /etc/fstab

pushd seagate-tools/performance/PerfLine
ansible-playbook -i inventories/perfline_hosts/hosts run_perfline.yml -v
popd

echo PerfLine has been installed successfully
