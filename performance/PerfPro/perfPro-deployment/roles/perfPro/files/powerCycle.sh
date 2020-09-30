#!/bin/bash
if [ -z $1 ]
then
        echo "add BMC IP address. usage ./reimage.sh <BMC IP address>"
else
        ipmitool -I lanplus -H $1 -U admin -P admin! chassis bootdev pxe
        ipmitool -I lanplus -H $1 -U admin -P admin! chassis power cycle
fi

