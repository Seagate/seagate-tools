#!/bin/sh
fo_t_sum=0
fb_t_sum=0
failover_failback() {
    t1=$(date '+%s')
    pcs node standby 'srvnode-2'
    while ! pcs status | grep standby > /dev/null; do
        sleep 1
    done
    while ! systemctl --quiet is-active hare-hax-c2 ; do
        sleep 1
    done
    s3_on_c1=`pcs status | grep s3server-c1 | grep Started | wc -l`
    while [[ $s3_on_c1 -lt 11 ]]; do
        s3_on_c1=`pcs status | grep s3server-c1 | grep Started | wc -l`
    done
    s3_on_c2=`pcs status | grep s3server-c2 | grep Started | wc -l`
    if [ $s3_on_c2 -ne 0 ]; then
        echo "Test failed."
        exit 1
    fi
    t2=$(date '+%s')
    sleep 60
    t3=$(date '+%s')
    pcs node unstandby 'srvnode-2'
    while pcs status | grep standby > /dev/null; do
        sleep 1
    done
    while systemctl --quiet is-active hare-hax-c2; do
        sleep 1
    done
    s3_on_c1=`pcs status | grep s3server-c1 | grep Started | wc -l`
    s3_on_c2=`pcs status | grep s3server-c2 | grep Started | wc -l`
    while [[ $s3_on_c1 -lt 11 || $s3_on_c2 -lt 11 ]]; do
        s3_on_c1=`pcs status | grep s3server-c1 | grep Started | wc -l`
        s3_on_c2=`pcs status | grep s3server-c2 | grep Started | wc -l`
    done
    t4=$(date '+%s')
    fo_t=`expr $t2 - $t1`
    fb_t=`expr $t4 - $t3`
    fo_t_sum=`expr $fo_t_sum + $fo_t`
    fb_t_sum=`expr $fb_t_sum + $fb_t`
    printf '\n|%-14s|%-18s|%-14s|%-18s|%-13s|%-13s|' $(date --date=@$t1 '+%T') $(date --date=@$t2 '+%T') $(date --date=@$t3 '+%T') $(date --date=@$t4 '+%T') $fo_t $fb_t
    printf '\n|-----------------------------------------------------------------------------------------------|'
    echo
}

i=1
printf '\n|-----------------------------------------------------------------------------------------------|'
printf '\n|Stopped node-2|Failover Completed|Started node-2|Failback completed|Failover time|Failback time|'
printf '\n|-----------------------------------------------------------------------------------------------|'
for i in {1..20}; do
    failover_failback
done
fo_t_avg=`expr $fo_t_sum / $i`
fb_t_avg=`expr $fb_t_sum / $i`
printf '\nAvg. failover time = %s sec' $fo_t_avg
printf '\nAvg. failback time = %s sec' $fb_t_avg
echo

