#! /bin/bash
if [ ! `rpm -qa | grep 'golang-1.11.5-1.el7.x86_64'` > /dev/null 2>&1 ] ; then
   yum install go -y
else
   echo "golang is already installed"
fi
if [ ! -f "/root/go/bin/hsbench" ] ; then
   echo "Installing hsbench tools"
   cd ~; go get github.com/markhpc/hsbench
   cd /root/go/src/github.com/markhpc/hsbench; go build
else
   echo "HSbenchmark Tools is already configured"
fi

