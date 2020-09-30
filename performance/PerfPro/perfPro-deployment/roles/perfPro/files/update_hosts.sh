#! /bin/bash

# ./update_hosts client1 server1 server2
File=/etc/ansible/hosts
yes | cp hosts.bak /etc/ansible/hosts >/dev/null 2>&1
#if grep -q perfproclientserver "$File"; then
#  sed -i '/\[perfproclientserver\]/,+11d' $File
#else
#  echo -e "\n[perfproclientserver]" > $File 
#fi
#if ! grep -q perfpros3server "$File"; then
#  echo -e "\n[perfpros3server]" >> $File 
#fi
#if ! grep -q perfproallserver "$File"; then
#  echo -e "\n[perfproallserver]" >> $File 
#fi

sed -i "/^\[perfproclientserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[perfpros3server\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[perfpros3server\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[perfproallserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[perfproallserver\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" $File
sed -i "/^\[perfproallserver\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" $File
