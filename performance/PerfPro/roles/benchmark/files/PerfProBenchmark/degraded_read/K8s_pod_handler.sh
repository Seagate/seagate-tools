#!/bin/bash

effected_replica=$(kubectl get deployment | grep 'cortx-data' | awk 'NR==1{print$1}')

if [ $1 == "down" ]
then
kubectl scale --replicas=0 deployment/$effected_replica
elif [ $1 == "up" ]
then
kubectl scale --replicas=1 deployment/$effected_replica
fi


