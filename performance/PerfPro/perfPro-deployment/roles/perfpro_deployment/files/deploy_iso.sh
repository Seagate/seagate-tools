#!/bin/expect -f
# ./deploy.sh build node1 node2 pass

spawn provisioner auto_deploy \
    --console-formatter full \
    --logfile \
    --logfile-filename /var/log/seagate/provisioner/setup.log \
    --source iso --config-path /root/config.ini \
    --ha \
    --iso-cortx /opt/isos/[lindex $argv 0] \
    --iso-os /opt/isos/[lindex $argv 1] \
    srvnode-1:[lindex $argv 2] \
    srvnode-2:[lindex $argv 3] 


set timeout 5400

expect {

    timeout {
        puts "Connection timed out"
        exit 1
    }

    "assword:" {
        send -- "[lindex $argv 4]\r"
        exp_continue
    }
}
