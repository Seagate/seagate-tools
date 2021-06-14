clientname=$(cat hosts|grep 'clientnode-1' | awk '{print $2}' |sed 's/.*=//')
for i in `ps -ef | grep -v grep | grep deploy_autoperf.yml |grep $clientname |awk '{ print $2 }'` 
do
kill -9 $i
echo  $i 'killed'
done
