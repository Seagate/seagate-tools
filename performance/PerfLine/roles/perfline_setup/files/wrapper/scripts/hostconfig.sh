#!/bin/bash
set -x

nodes=$1
flag=0

pdsh -S -w $nodes "hostname -i" | sort -n | awk '{print $2, $1}'| awk '{ $2="srvnode-"++i;}1' > hostsfile
for host in ${nodes//,/ }
do
   ssh $host "cat /etc/hosts | grep srvnode"
   flag=$?
   scp hostsfile $host:/root
done

if [ $flag -eq 1 ]
then
   pdsh -S -w $nodes "cat /root/testfile >> /etc/hosts"
   echo "/etc/hosts file configured successfully"
else
   echo "Host entry is already exist"
fi
