#!/bin/bash
for b in 1;
  do
    for s in 1Mb 5Mb 36Mb 64Mb 128Mb 256Mb;
      do
        ./s3cosbench_benchmark.sh -nc "100" -ns "1000" -s $s -b $b -w mixed -t 600 -sm 5;
        sleep 10;
      done
  done   

for b in 10 50;
  do
    for s in 1Mb 5Mb 36Mb 64Mb 128Mb 256Mb;
      do
        ./s3cosbench_benchmark.sh -nc "100" -ns "100" -s $s -b $b -w mixed -t 600 -sm 5;
        sleep 10;
      done
  done

