#!/bin/expect -f
# ./deploy.sh build node1 node2 pass
spawn provisioner auto_deploy \
    --console-formatter full \
    --logfile \
    --logfile-filename /var/log/seagate/provisioner/setup.log \
    --source iso --config-path /root/config.ini \
    --ha --pypi-repo \
    --iso-cortx /root/cortx-1.0.0-[lindex $argv 0]-single.iso \
    srvnode-1:[lindex $argv 1]\
    srvnode-2:[lindex $argv 2] \

set timeout 5400

expect {

    timeout {
        puts "Connection timed out"
        exit 1
    }

    "assword:" {
        send -- "[lindex $argv 3]\r"
        exp_continue
    }
}
