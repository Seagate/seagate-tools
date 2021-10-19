#! /bin/bash
if [ ! -f "/root/go/bin/hsbench" ] ; then
   echo "Installing hsbench tools"
   cd ~; go get github.com/markhpc/hsbench
   cd /root/go/src/github.com/markhpc/hsbench; go build
else
   echo "HSbenchmark Tools is already configured"
fi
