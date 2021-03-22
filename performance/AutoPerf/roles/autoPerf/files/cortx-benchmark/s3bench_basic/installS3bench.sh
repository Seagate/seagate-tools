#! /usr/bin/bash
if [ ! `rpm -qa | grep 'golang-1.11.5-1.el7.x86_64'` > /dev/null 2>&1 ] ; then
   yum install go -y
else
   echo "golang is already installed"
fi
if [ ! -f "/root/go/bin/s3bench.old" ] ; then
   echo "Installing s3bench tools"
   cd ~; go get github.com/igneous-systems/s3bench
   yes | cp ~/go/bin/s3bench ~/go/bin/s3bench.old
else
   yes | cp ~/go/bin/s3bench.old ~/go/bin/s3bench
   echo "S3benchmark Tools is already configured"
fi

