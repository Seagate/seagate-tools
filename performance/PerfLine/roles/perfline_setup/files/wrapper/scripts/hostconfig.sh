#!/bin/bash
set -x

nodes=$1

pdsh -S -w $nodes "hostname -i" | sort -n | awk '{print $2, $1}'| awk '{ $2="srvnode-"++i;}1' > hostsfile
for host in ${nodes//,/ }
do
   ssh $host "cat /etc/hosts | grep srvnode"
   flag=$?
   if [ $flag -eq 0 ]
   then
       echo "Host entry is already exist in $host"
   else
       scp hostsfile $host:/tmp
       ssh $host "cat /tmp/hostsfile >> /etc/hosts"
       echo "/etc/hosts file configured successfully"
   fi
done
