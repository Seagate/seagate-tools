clientname=$(cat hosts|grep 'clientnode-1' | awk '{print $2}' |sed 's/.*=//')

for i in `ps -ef | grep -v grep | grep deploy_autoperf.yml |grep $clientname |awk '{ print $2 }'` 
do
kill $i
if [ $? -ne 0 ]
then 
sleep 5
kill -9 $i
fi
echo  $i 'killed'
done

