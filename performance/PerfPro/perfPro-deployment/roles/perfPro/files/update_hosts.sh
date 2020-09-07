#! /bin/bash

# ./update_hosts client1 server1 server2

yes | cp hosts.bak /etc/ansible/hosts >/dev/null 2>&1
sed -i "/^\[clientserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
sed -i "/^\[s3server\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
sed -i "/^\[s3server\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
sed -i "/^\[allserver\]/a serverclient ansible_host=$1 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
sed -i "/^\[allserver\]/a serverprimary ansible_host=$2 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
sed -i "/^\[allserver\]/a serversecondary ansible_host=$3 ansible_connection=ssh ansible_user=root" /etc/ansible/hosts
