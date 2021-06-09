#! /bin/bash

echo "$1" > driver-nodes-list
if [ ! -d "/root/cos" ] ; then
   echo "Installing cosbench"
   sh cosbench.sh install --controller $1 --drivers driver-nodes-list
   sh cosbench.sh configure --controller $1 --drivers driver-nodes-list 
   sh cosbench.sh start --controller $1 --drivers driver-nodes-list
else
   echo -e "cosbench tools is already installed on $1"
fi

ps -ef | grep "driver-tomcat-server.xml" > /dev/null
status=$?
if [ $status -eq 0 ]; then
   echo "cosbench is running on $1"
else
   echo "Starting cosbench..."
   sh cosbench.sh start --controller $1 --drivers driver-nodes-list
fi
