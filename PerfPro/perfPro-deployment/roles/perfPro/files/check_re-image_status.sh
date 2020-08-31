#! /usr/bin/bash
flag=true
host1=$1
host2=$2
while $flag
do
       

       flag1=`curl --user srvcqa1:Y2ecGgVJsK57dYdm -k -H "Content-Type:application/json" -H "Accept:application/json" https://ssc-satellite1.colo.seagate.com/api/v2/hosts/$host1 | jq -r '.build'`
       if $flag1    
       then
           echo -e "$flag1: \t Re-image is in progress for $host1"
       else
           echo -e "$flag1: \t Reimage successful $host1"
       fi

       flag2=`curl --user srvcqa1:Y2ecGgVJsK57dYdm -k -H "Content-Type:application/json" -H "Accept:application/json" https://ssc-satellite1.colo.seagate.com/api/v2/hosts/$host2 | jq -r '.build'`
       if $flag2
       then
           echo -e "$flag2: \t Re-image is in progress for $host2"
       else
           echo -e "$flag2: \t Reimage successful $host2"
       fi
       
       if [ ! $flag1 == 'true' ] & [ ! $flag2 == 'true' ]
       then
           echo "Both are reimaged"
           flag=false
       else
           sleep 300 
       fi
done
