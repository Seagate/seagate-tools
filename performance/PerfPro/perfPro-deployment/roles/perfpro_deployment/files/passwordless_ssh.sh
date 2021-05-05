#!/bin/expect -f
# ./passwordless_ssh.sh node username pass
spawn ssh-copy-id -o "StrictHostKeyChecking=no" [lindex $argv 0]@[lindex $argv 1]
set timeout 10
expect {
    timeout {
        puts "Connection timed out"
        exit 1
    }

    "yes/no" {
        send "yes\r"
        exp_continue
    }

    "assword:" {
        send -- "[lindex $argv 2]\r"
        exp_continue
    }
}
