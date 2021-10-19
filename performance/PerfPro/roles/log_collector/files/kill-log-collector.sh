for i in `ps -ef | grep -v grep | grep ansible.log | awk '{ print $2 }'`; do kill -9 $i; done
