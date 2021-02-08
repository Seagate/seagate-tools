#! /bin/bash
# ./update_hosts server1 server2
yes | cp inventories/perfpro_deployment/hosts.bak inventories/perfpro_deployment/hosts
sed -i "s/<SRVNODE-1_HOST>/$1/g" inventories/perfpro_deployment/hosts
sed -i "s/<SRVNODE-2_HOST>/$2/g" inventories/perfpro_deployment/hosts
sed -i "s/<CLIENT_HOST>/$3/g" inventories/perfpro_deployment/hosts