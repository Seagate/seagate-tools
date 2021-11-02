./run_benchmark.sh -b 1 -o 1000 -s "4Kb,100Kb,1Mb,5Mb,36Mb,64Mb,128Mb,256Mb" -t 100 -d 600
sleep 10
./run_benchmark.sh -b 10 -o 1000 -s "4Kb,100Kb,1Mb,5Mb,36Mb,64Mb,128Mb,256Mb" -t 100 -d 600
sleep 10
./run_benchmark.sh -b 50 -o 5000 -s "4Kb,100Kb,1Mb,5Mb,36Mb,64Mb,128Mb,256Mb" -t 100 -d 600
sleep 10

