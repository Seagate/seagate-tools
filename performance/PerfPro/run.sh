#!/bin/bash

curdir="$(dirname $0)"

cd $curdir

if rpm -qa | grep ansible > /dev/null
  then
    echo "Ansible is already installed"
  else
    echo "Installing ansible"
    yum install -y ansible
fi

if [[ "$1" == "sanity" ]]
  then
    ansible-playbook perfpro.yml -i inventories/hosts -v --extra-vars '{ "EXECUTION_TYPE" : "sanity" }'
  else
    ansible-playbook perfpro.yml -i inventories/hosts -v
fi

