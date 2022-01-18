#!/bin/bash
mylimit=`cat ~/.bashrc | grep 'ulimit' | awk '{print $3}'`
if [ -z $mylimit ]
  then
    echo "*** Appending ulimit to bashrc ***"
    echo "ulimit -n 100000" >> ~/.bashrc
    echo "*** Appended ***"
elif [ $mylimit -eq 100000 ]
  then
    echo "*** Ulimit is already set to 100000 ***"
    echo "*** Nothing to modify ***"
else
    echo "*** Modifying ulimit value in bashrc ***"
    sed -i "s/ulimit -n $mylimit/ulimit -n 100000/" ~/.bashrc
    echo "*** Modified ***"
fi

echo "*** Loading bashrc ***"
echo "*** Loaded ***"
source ~/.bashrc
echo "*** Old ulimit value: $mylimit ***"
echo "*** New ulimit value: `ulimit -n` ***"

