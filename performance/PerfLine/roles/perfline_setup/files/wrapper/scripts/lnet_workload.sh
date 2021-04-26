#!/bin/bash
set -e
set -x

NODES=$1
OPS_TYPES=$2

for i in ${OPS_TYPES//,/ }
do
     echo $i : $NODES
     pdsh -S -w $NODES modprobe lnet_selftest
     lnet_ips=$(pdsh -S -w $NODES 'lctl list_nids' | cut -d '.' -f4 | cut -d '@' -f1 | paste -sd ',')
     lnet_net=$(pdsh -S -w $NODES 'lctl list_nids' | cut -d ' ' -f2 | cut -d '.' -f1,2,3 | head -1)
     export LST_SESSION=$$
     lst new_session threenode$i
     lst add_group client $lnet_net.[$lnet_ips]@o2ib
     lst add_group server $lnet_net.[$lnet_ips]@o2ib
     if [ "$i" != "ping" ]
     then
         lst add_batch bulk_$i
         lst add_test --concurrency 8 --batch bulk_$i --from client --to server brw $i size=1M
         lst run bulk_$i
         lst stat client server & sleep 30; kill $!
         lst stop bulk_$i
     else
         lst add_batch $i
         lst add_test --concurrency 128 --batch $i --from client --to server $i
         lst run $i
         lst stat client server & sleep 60; kill $!
         lst stop $i
     fi
     lst end_session
     
     pdsh -S -w $NODES rmmod lnet_selftest
done
