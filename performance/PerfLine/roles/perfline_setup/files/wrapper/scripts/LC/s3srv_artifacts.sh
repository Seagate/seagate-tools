
# public interface

function create_s3_account()
{
    # create an s3 account
    ssh $PRIMARY_NODE "$SCRIPT_DIR/../../s3account/lc_create_user.sh"

    # configure aws utility
    ssh $PRIMARY_NODE "$SCRIPT_DIR/../../s3account/lc_setup_aws.sh"
}

function save_s3app_configs()
{
    mkdir -p $S3_ARTIFACTS_DIR
    pushd $S3_ARTIFACTS_DIR
    save_s3_configs
    popd
}

function save_s3app_artifacts()
{
    mkdir -p $S3_ARTIFACTS_DIR
    pushd $S3_ARTIFACTS_DIR
    save_s3srv_artifacts
    popd
}

# implementation

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
        pod=`ssh $PRIMARY_NODE "kubectl get pod -o wide" | grep $srv | grep $CORTX_SERVER_POD_PREFIX | awk '{print $1}'`
        containers=`ssh $PRIMARY_NODE "kubectl get pods $pod -o jsonpath='{.spec.containers[*].name}'" | tr ' ' '\n' | grep s3 | grep -v haproxy | grep -v auth | grep -v consumer`
        mkdir -p $srv
        pushd $srv

        for cont in $containers ; do
            mkdir -p $cont
            pushd $cont

            # Copy config
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
        dirs=`find $LOCAL_MOUNT_POINT/var/log/s3/ -name "*$serv*" -exec realpath {} \;`
        
        for d in $dirs ; do
            uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
            mkdir -p $uid
            pushd $uid

            cp -r $d ./
	    
            popd 		# $uid
        done

        popd			# $name
    done

    # Copy haproxy
    mkdir -p haproxy
    pushd haproxy
    files=`find $LOCAL_MOUNT_POINT/var/log -name "haproxy.log"`

    for f in $files; do
        uid=`echo $f | awk -F'/' '{print $(NF-2)}'`
        mkdir -p $uid
        pushd $uid

        cp -r $f ./

        popd        # $uid
    done

    popd            # haproxy

    # Copy auth server logs
    local auth_logs="/var/log/cortx/auth"
    mkdir -p auth
    pushd auth
    cp -r $LOCAL_MOUNT_POINT/var/log/auth ./
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

        dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" )`
        for d in $dirs ; do
            files=`( ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME ls -1 $d" ) | grep m0trace | grep -v txt`
            for file in $files; do
                ssh $PRIMARY_NODE "nohup docker exec $DOCKER_CONTAINER_NAME m0trace -i $d/$file -o $d/$file.txt &" &
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
        dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" )`
        for d in $dirs ; do
            uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
            # Assuming `/share` at the beginning of the string 
            rel_path="${d:6}"

            mkdir -p $uid
            pushd $uid
            scp -r $PRIMARY_NODE:$LOCAL_MOUNT_POINT/$rel_path/m0trace* ./
            popd		# $uid
        done
        popd # $name
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
    pid=$S3_INIT_PID
    lines_n=`cat ../s3server_map | wc -l`
    for i in $(seq 1 $lines_n) ; do 
        read h pod cont serv trace addb log <<< `awk "NR==$i" ../s3server_map`

        dirs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME find /share/var/log/motr -name \"*$serv*\" -exec realpath {} \;" ) `

        for d in $dirs ; do
            uid=`echo $d | awk -F'/' '{print $(NF-1)}'`
            stobs=`( ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME ls -1 $d" ) | grep addb`

            for st in $stobs; do
                addb_stob="$d/$st/o/100000000000000:2"
                echo $h $pod $cont $serv $addb_stob $uid $pid >> addb_mapping
                ssh $PRIMARY_NODE "docker exec $DOCKER_CONTAINER_NAME /bin/bash -c \"m0addb2dump -f -p /opt/seagate/cortx/s3/addb-plugin/libs3addbplugin.so -- $addb_stob\"" > dumpc_${pid}.txt &

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
