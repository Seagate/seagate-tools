#! /usr/bin/bash
if [ ! `rpm -qa | grep 'golang-1.11.5-1.el7.x86_64'` > /dev/null 2>&1 ] ; then
   yum install go -y
else
   echo "golang is already installed"
fi
if [ ! -f "/root/go/bin/s3bench.old" ] ; then
   echo "Installing s3bench tools"
   cd ~; go get github.com/igneous-systems/s3bench
   cd /root/go/src/github.com/igneous-systems/s3bench; go build
   yes | cp /root/go/src/github.com/igneous-systems/s3bench/s3bench ~/go/bin/s3bench.old
else
   cp ~/go/bin/s3bench.old s3bench
   echo "S3benchmark Tools is already configured"
fi

