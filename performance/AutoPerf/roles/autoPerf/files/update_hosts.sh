#! /bin/bash

# ./update_hosts client1 server1 server2

#yes | cp hosts.bak /etc/ansible/hosts >/dev/null 2>&1
File=/etc/ansible/hosts
yes | cp hosts.bak /etc/ansible/hosts >/dev/null 2>&1
#if grep -q "\[clientserver\]" "$File"; then
#  sed -i "/\[clientserver\]/,+12d" $File
#else
#  echo -e "\n[clientserver]" >> $File
#fi
#if ! grep -q "\[s3server\]" "$File"; then
#  echo -e "\n[s3server]" >> $File
#fi
#if ! grep -q "\[allserver\]" "$File"; then
#  echo -e "\n[allserver]" >> $File
#fi

sed -i "/^\[clientserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[s3server\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[s3server\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[allserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[allserver\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[allserver\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" $File
