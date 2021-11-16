CORTX_K8S_REPO="/root/cortx-k8s"
K8S_SCRIPTS_DIR="$CORTX_K8S_REPO/k8_cortx_cloud"

HAX_CONTAINER="cortx-motr-hax"
LOCAL_MOUNT_POINT='/mnt/fs-local-volume/etc/gluster'
DOCKER_IMAGE_NAME="perfline_cortx"
MOTR_ARTIFACTS_DIR="m0d"
S3_ARTIFACTS_DIR="s3server"


function run_cmd_in_container()
{
    local pod="$1"
    local container="$2"
    shift
    shift

    ssh $PRIMARY_NODE "kubectl exec $pod -c $container -- $@"
}

function is_cluster_online()
{
    local all_services=$(run_cmd_in_container $PRIMARY_POD $HAX_CONTAINER hctl status | grep "\s*\[.*\]")
    local srvc_states=$(echo "$all_services" | grep -E 's3server|ioservice|confd|hax' | awk '{print $1}')
    for state in $srvc_states; do
        if [[ "$state" != "[started]" ]]; then
            return 1
        fi
    done
    return 0
}

function stop_cluster() {
    echo "Stop LC cluster"

    # let's try to wait for m0d to complete all operations
    sleep 120

    ssh $PRIMARY_NODE "cd $K8S_SCRIPTS_DIR && ./destroy-cortx-cloud.sh"
}

function cleanup_logs() {
    echo "Remove m0trace/addb/log files from LC cluster"
    $EX_SRV 'rm -rf /etc/3rd-party/openldap /var/data/3rd-party/*' || true
    $EX_SRV 'rm -rf /mnt/fs-local-volume/local-path-provisioner/*' || true
    $EX_SRV 'rm -rf /mnt/fs-local-volume/etc/gluster/var/log/cortx/*' || true
}

function detect_primary_pod()
{
    PRIMARY_POD=$(ssh $PRIMARY_NODE "kubectl get pod -o wide" \
         | grep 'cortx-data-pod' \
         | grep $PRIMARY_NODE \
         | awk '{print $1}')

    if [[ -z "$PRIMARY_POD" ]]; then
        echo "detection of POD failed"
        exit 1
    fi
}

function restart_cluster() {
    echo "Restart LC cluster (PODs)"
#    ssh $PRIMARY_NODE "cd $K8S_SCRIPTS_DIR && ./deploy-cortx-cloud.sh"
    detect_primary_pod
    wait_for_cluster_start

    ssh $PRIMARY_NODE "kubectl get pod"    
}

function wait_for_cluster_start() {
    echo "wait for cluster start"

    while ! is_cluster_online $PRIMARY_NODE
    do
        sleep 5
    done
    
    # $EX_SRV $SCRIPT_DIR/wait_s3_listeners.sh $S3SERVER
    # sleep 300
}

function save_motr_configs() {
    local config_dir="configs"

    local pod
    local containers
    local mapping
    local service
    local trace_dir
    local addb_dir

    mkdir -p $config_dir
    pushd $config_dir
    
    for srv in $(echo $NODES | tr ',' ' '); do
 	    pod=`ssh $PRIMARY_NODE "kubectl get pod -o wide" | grep $srv | grep cortx-data-pod | awk '{print $1}'`
	    containers=`ssh $PRIMARY_NODE "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep cortx-motr-ios`
        mkdir -p $srv
	    pushd $srv

	    for cont in $containers ; do
	        mkdir -p $cont
	        pushd $cont

	        # Copy motr config
	        ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/sysconfig/motr" > motr
	        ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/cortx/cluster.conf" > cluster.conf
	    
	        # Gather metadata
	        service=`ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- ps auxww" | grep m0d | tr ' ' '\n' | grep -A1 -- "-f" | tail -n1 | tr -d '<' | tr -d '>'`

	        trace_dir=`cat motr | grep MOTR_M0D_TRACE | grep -v "#"`
	        addb_dir=`cat motr | grep MOTR_M0D_ADDB | grep -v "#"`

	        mapping="${srv} ${pod} ${cont} ${service} ${trace_dir} ${addb_dir}\n${mapping}"
	        popd		# $cont
	    done
	    popd			# $srv
    done

    popd			# $config_dir
    
    printf "$mapping" > ioservice_map
}

function save_s3_configs() {
    local config_dir="configs"

    local pod
    local containers
    local s3mapping
    local service
    local log_dir
    local trace_dir
    local addb_dir

    mkdir -p $config_dir
    pushd $config_dir
    
    for srv in $(echo $NODES | tr ',' ' '); do
	pod=`ssh $PRIMARY_NODE "kubectl get pod -o wide" | grep $srv | grep cortx-data-pod | awk '{print $1}'`
	containers=`ssh $PRIMARY_NODE "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep s3 | grep -v haproxy | grep -v auth | grep -v consumer`
        mkdir -p $srv
	pushd $srv

	for cont in $containers ; do
	    mkdir -p $cont
	    pushd $cont

	    # Copy motr config
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/cortx/s3/conf/s3config.yaml" > s3config.yaml
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /opt/seagate/cortx/s3/s3startsystem.sh" > s3startsystem.sh
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/cortx/cluster.conf" > cluster.conf
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/hosts" > hosts
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/haproxy/haproxy.cfg" > haproxy.cfg
	    
	    trace_dir=`cat s3config.yaml | grep S3_DAEMON_WORKING_DIR | awk '{print $2}'`
	    addb_dir=`echo $trace_dir`
	    log_dir=`cat s3config.yaml | grep S3_LOG_DIR | awk '{print $2}'`

	    echo ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- ps auxww"
	    
	    # Gather process FID
	    service=`ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- ps auxww" | grep s3server | grep motr | tr ' ' '\n' | grep -A1 "processfid" | tail -n1`
	    service=`echo $service | tr -d '<' | tr -d '>'`

	    s3mapping="${srv} ${pod} ${cont} ${service} ${trace_dir} ${addb_dir} ${log_dir}\n${s3mapping}"
	    popd		# $cont
	done

	containers=`ssh $PRIMARY_NODE "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep haproxy`
	for cont in $containers ; do
	    mkdir -p $cont
	    pushd $cont
	    ssh $PRIMARY_NODE "kubectl exec $pod -c $cont -- cat /etc/cortx/s3/haproxy.cfg" > haproxy.cfg
	    popd
	done

	popd			# $srv
    done

    popd			# $config_dir
    
    printf "$s3mapping" > s3server_map
}


function save_cluster_status() {
    run_cmd_in_container $PRIMARY_POD $HAX_CONTAINER hctl status > hctl-status.stop

    mkdir -p $MOTR_ARTIFACTS_DIR
    pushd $MOTR_ARTIFACTS_DIR
    save_motr_configs
    popd 			# $MOTR_ARTIFACTS_DIR

    mkdir -p $S3_ARTIFACTS_DIR
    pushd $S3_ARTIFACTS_DIR
    save_s3_configs
    popd 			# $S3_ARTIFACTS_DIR
}

function copy_kube_config()
{
    for node in ${NODES//,/ }
    do 
       if [ "$node" != "$PRIMARY_NODE" ];
       then
           ssh $node "mkdir -p /root/.kube"
           ssh $PRIMARY_NODE "scp /root/.kube/config $node:/root/.kube/config"
        fi
    done
}


function prepare_cluster() {
    copy_kube_config
    # update /etc/hosts
    local ip=$(ssh $PRIMARY_NODE 'kubectl get pod -o wide | grep $(hostname) | grep cortx-data' | awk '{print $6}')

    if [ -z "$ip" ]; then
        echo "s3 ip detection failed"
        exit 1
    fi

    ssh $PRIMARY_NODE 'sed -i "/s3.seagate.com/d" /etc/hosts'
    ssh $PRIMARY_NODE 'sed -i "/sts.seagate.com/d" /etc/hosts'
    ssh $PRIMARY_NODE 'sed -i "/iam.seagate.com/d" /etc/hosts'
    ssh $PRIMARY_NODE "echo $ip s3.seagate.com sts.seagate.com iam.seagate.com >> /etc/hosts"

    # create an s3 account
    ssh $PRIMARY_NODE "$SCRIPT_DIR/../../s3account/lc_create_user.sh"

    # configure aws utility
    ssh $PRIMARY_NODE "$SCRIPT_DIR/../../s3account/lc_setup_aws.sh"
}

function collect_stat_data()
{
    run_cmd_in_container $PRIMARY_POD $HAX_CONTAINER cat /etc/cortx/cluster.conf > cluster.conf

    for srv in $(echo $NODES | tr ',' ' '); do
        local cluster_conf="/tmp/cluster.conf"
        local disks_map="/tmp/cortx_disks_map"
        local hostname_short=$(echo $srv | awk -F '.' '{print $1}')
        scp cluster.conf $srv:$cluster_conf
        ssh $srv "$SCRIPT_DIR/LC/get_disks_map.py $cluster_conf $hostname_short > $disks_map"
    done
}

function save_motr_traces() {
    local pod
    local cont
    local serv
    local trace 
    local addb
    local lines_n
    local rel_path
    local files
    local dirs
    local uid
    local name

    set +e

    lines_n=`cat ../ioservice_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb <<< `awk "NR==$i" ../ioservice_map`
	
	eval "$trace/m0d-$serv"
	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $MOTR_M0D_TRACE_DIR/../../../ -name \"*$serv*\" -exec realpath {} \;" ) | grep trace`
	for d in $dirs ; do
	    files=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME ls -1 $d" ) | grep m0trace | grep -v txt`
	    for file in $files; do
		ssh $PRIMARY_NODE "nohup docker exec $DOCKER_IMAGE_NAME m0trace -i $d/$file -o $d/$file.txt &" &
	    done
	done
    done

    # Wait until all async m0traces finish
    wait

    # Copy traces to results folder
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb <<< `awk "NR==$i" ../ioservice_map`

	eval "$trace/m0d-$serv"
	name="m0d-$serv"

	mkdir -p $name
	pushd $name
	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $MOTR_M0D_TRACE_DIR/../../../ -name \"*$serv*\" -exec realpath {} \;" ) | grep trace`
	for d in $dirs ; do
	    uid=`echo $d | awk -F'/' '{print $(NF-2)}'`

	    mkdir -p $uid
	    pushd $uid
	    # Assuming `/share` at the beginning of the string 
	    rel_path="${d:6}"
	    scp -r $PRIMARY_NODE:$LOCAL_MOUNT_POINT/$rel_path/* ./
	    popd		# $uid
	done
	popd			# $name
    done

    set -e
}

function save_motr_addb() {
    local pod
    local cont
    local serv
    local trace 
    local addb
    local lines_n
    local rel_path
    local pid
    local addb_stob
    local uid

    set +e

    > addb_mapping
    pid=1
    lines_n=`cat ../ioservice_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb <<< `awk "NR==$i" ../ioservice_map`
	
	eval "$addb/m0d-$serv"
	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $MOTR_M0D_ADDB_STOB_DIR/../../../ -name \"*$serv*\" -exec realpath {} \;" ) | grep addb`

	for d in $dirs ; do
	    uid=`echo $d | awk -F'/' '{print $(NF-2)}'`

	    stobs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME ls -1 $d" ) | grep "addb-stob"`
	    for st in $stobs; do
		addb_stob="$d/$st/o/100000000000000:2"
		echo $h $pod $cont $serv $addb_stob $uid $pid >> addb_mapping
		
		ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME m0addb2dump -f -- \"$addb_stob\"" > dumps_${pid}.txt &
		
		((pid=pid+1))
	    done
	done
    done

    wait
    set -e
}

function generate_motr_m0play() {
    if ls dumps* &> /dev/null; then
        $TOOLS_DIR/../chronometry_v2/addb2db_multiprocess.sh --dumps ./dumps*
	mv m0play.db m0play.m0d.db
    fi
}

function start_docker_container() {
    local image

    set +e

    image=`(ssh $PRIMARY_NODE "docker images") | grep cortx-all | awk '{print $1":"$2}' | head -n1`
    ssh $PRIMARY_NODE "docker run -dit --name $DOCKER_IMAGE_NAME --mount type=bind,source=/mnt/fs-local-volume/etc/gluster,target=/share $image"
    set -e
}

function stop_docker_container() {
    set +e
    ssh $PRIMARY_NODE "docker stop $DOCKER_IMAGE_NAME"
    ssh $PRIMARY_NODE "docker rm $DOCKER_IMAGE_NAME"
    set -e
}

function save_motr_artifacts() {
    local ios_m0trace_dir="m0trace_ios"
    local dumps_dir="dumps"

    start_docker_container

    mkdir -p $ios_m0trace_dir
    pushd $ios_m0trace_dir
    if [[ -n $M0TRACE_FILES ]]; then
	save_motr_traces
    fi
    popd # $ios_motrace_dir

    mkdir -p $dumps_dir
    pushd $dumps_dir
    if [[ -n $ADDB_DUMPS ]]; then
	save_motr_addb
	generate_motr_m0play
    fi
    popd # $dumps_dir

    stop_docker_container
}

function save_s3srv_logs() {
    local pod
    local cont
    local serv
    local trace 
    local addb
    local lines_n
    local rel_path
    local files
    local dirs
    local uid
    local name
    local log_dir
    
    lines_n=`cat ../s3server_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb log <<< `awk "NR==$i" ../s3server_map`

	name="s3server-$serv"
	mkdir -p $name
	pushd $name
	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $log/../ -name \"*$serv*\" -exec realpath {} \;" )`
	for d in $dirs ; do
	    uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
	    mkdir -p $uid
	    pushd $uid

	    rel_path="${d:6}"
	    scp -r $PRIMARY_NODE:$LOCAL_MOUNT_POINT/$rel_path/* ./
	    
	    popd 		# $uid
	done
	popd			# $name
    done

    # Copy haproxy
    mkdir -p haproxy
    pushd haproxy
    files=`ssh $PRIMARY_NODE find $LOCAL_MOUNT_POINT -name "haproxy.log"`
    for f in $files; do
	uid=`echo $f | awk -F'/' '{print $(NF-2)}'`
	mkdir -p $uid
	pushd $uid

	scp -r $PRIMARY_NODE:$f ./
	
	popd 		# $uid
    done
    popd			# haproxy

    # Copy auth server logs
    local auth_logs="/var/log/cortx/auth"
    mkdir -p auth
    pushd auth
    scp -r $PRIMARY_NODE:$LOCAL_MOUNT_POINT/$auth_logs/* ./
    popd 			# auth
}

function save_s3_traces() {
    local pod
    local cont
    local serv
    local trace 
    local addb
    local lines_n
    local rel_path
    local files
    local dirs
    local uid
    local name
    
    set +e

    lines_n=`cat ../s3server_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb log <<< `awk "NR==$i" ../s3server_map`

	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $trace/.. -name \"*$serv*\" -exec realpath {} \;" )`
	for d in $dirs ; do
	    files=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME ls -1 $d" ) | grep m0trace | grep -v txt`
	    for file in $files; do
		ssh $PRIMARY_NODE "nohup docker exec $DOCKER_IMAGE_NAME m0trace -i $d/$file -o $d/$file.txt &" &
		
	    done
	done
    done

    # Wait until all async m0traces finish
    wait

    # Copy traces to results folder
    for i in $(seq 1 $lines_n) ; do
	read h pod cont serv trace addb log <<< `awk "NR==$i" ../s3server_map`

	name="s3server-$serv"

	mkdir -p $name
	pushd $name
	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $trace/.. -name \"*$serv*\" -exec realpath {} \;" ) `
	for d in $dirs ; do
	    uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
	    # Assuming `/share` at the beginning of the string 
	    rel_path="${d:6}"

	    mkdir -p $uid
	    pushd $uid
	    scp -r $PRIMARY_NODE:$LOCAL_MOUNT_POINT/$rel_path/m0trace* ./
	    popd		# $uid
	done
	popd			# $name
    done
    set -e
}

function save_s3_addb() {
    local pod
    local cont
    local serv
    local trace 
    local addb
    local lines_n
    local rel_path
    local pid
    local addb_stob
    local uid

    set +e

    > addb_mapping
    pid=10001
    lines_n=`cat ../s3server_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
	read h pod cont serv trace addb log <<< `awk "NR==$i" ../s3server_map`

	dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME find $addb/.. -name \"*$serv*\" -exec realpath {} \;" ) `
	for d in $dirs ; do
	    uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
	    stobs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME ls -1 $d" ) | grep addb`
	    for st in $stobs; do
		addb_stob="$d/$st/o/100000000000000:2"
		echo $h $pod $cont $serv $addb_stob $uid $pid >> addb_mapping
		
		ssh $PRIMARY_NODE "docker exec $DOCKER_IMAGE_NAME m0addb2dump -f -p /opt/seagate/cortx/s3/addb-plugin/libs3addbplugin.so -- \"$addb_stob\"" > dumpc_${pid}.txt &
		
		((pid=pid+1))
	    done
	done
    done

    wait
    set -e
}

function generate_s3_m0play() {
    if ls dumpc* &> /dev/null; then
        $TOOLS_DIR/../chronometry_v2/addb2db_multiprocess.sh --dumps ./dumpc*
	mv m0play.db m0play.s3.db
    fi
}

function save_s3srv_artifacts() {
    local log_dir="log"
    local m0trace_dir="m0trace"
    local dumps_dir="dumps"
    
    start_docker_container
    
    mkdir -p $log_dir
    pushd $log_dir
    save_s3srv_logs
    popd			# $log_dir

    if [[ -n $M0TRACE_FILES ]]; then
	mkdir -p $m0trace_dir
	pushd $m0trace_dir
	save_s3_traces
	popd 			# $m0trace_dir
    fi

    if [[ -n $ADDB_DUMPS ]]; then
	mkdir -p $dumps_dir
	pushd $dumps_dir
	save_s3_addb
	generate_s3_m0play
	popd			# $dumps_dir
    fi
    
    stop_docker_container
}

function collect_artifacts() {
    local m0d="$MOTR_ARTIFACTS_DIR"
    local s3srv="$S3_ARTIFACTS_DIR"
    local stats="stats"

    echo "Collect artifacts"

    mkdir -p $stats
    pushd $stats
    save_stats
    popd

    mkdir -p $m0d
    pushd $m0d
    save_motr_artifacts
    popd			# $m0d

    mkdir -p $s3srv
    pushd $s3srv
    save_s3srv_artifacts
    popd			# $s3server

    # Temporary disabled
    
    if [[ -n "$RUN_M0CRATE" ]]; then
         mkdir -p $M0CRATE_ARTIFACTS_DIR
         pushd $M0CRATE_ARTIFACTS_DIR
         save_m0crate_artifacts
         popd
    fi
    
    save_perf_results

    if [[ -n $ADDB_DUMPS ]]; then
        local m0playdb_parts="$m0d/dumps/m0play* $s3srv/dumps/m0play*"

        if [[ -n "$RUN_M0CRATE" ]]; then
            if ls $M0CRATE_ARTIFACTS_DIR/m0play* &> /dev/null; then
                m0playdb_parts="$m0playdb_parts $M0CRATE_ARTIFACTS_DIR/m0play*"
            else
                echo "m0play not found"
            fi
        fi

        $SCRIPT_DIR/merge_m0playdb $m0playdb_parts
        rm -f $m0playdb_parts
        $SCRIPT_DIR/../../chronometry_v2/fix_reqid_collisions.py --fix-db --db ./m0play.db
    fi

    if [[ -n $ADDB_ANALYZE ]] && [[ -f "m0play.db" ]]; then
        local m0play_path="$(pwd)/m0play.db"
        local stats_addb="$stats/addb"
        mkdir -p $stats_addb
        pushd $stats_addb
        $SCRIPT_DIR/process_addb_data.sh --db $m0play_path
        popd
    fi

    if [[ "$STAT_COLLECTION" == *"GLANCES"* ]]; then
        pushd $stats
        local srv_nodes=$(echo $NODES | tr ',' ' ')
        $SCRIPT_DIR/artifacts_collecting/process_glances_data.sh $srv_nodes
        popd
    fi
    
    # # generate structured form of stats
    # $SCRIPT_DIR/../stat/gen_run_metadata.py -a $(pwd) -o run_metadata.json
}
