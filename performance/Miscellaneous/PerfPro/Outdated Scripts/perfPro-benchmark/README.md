Installation and usage steps: 

	1. Install go language 

		$ yum install go -y

	2. Get the go language based s3bench,hsbench package 

		$ go get github.com/igneous-systems/s3bench 
		$ go get github.com/markhpc/hsbench
	    $ cd /root/go/src/github.com/igneous-systems/s3bench; go build
		$ cd /root/go/src/github.com/markhpc/hsbench; go build
	
	3. Untar BENCHMARK.tar.gz file, it will contain 3 benchmark wrapper script which is resposible for continuous S3 performance testing based on number of clients, number of samples, IOsize etc.

		$ tar -xzvf BENCHMARK.tar.gz
		
	4. Steps to run S3bench wrapper scripts
	
		$ cd allbenchmark/s3bench_basic;
		
		i). S3bench_basic wrapper script has designed for continuous S3 performance testing based on different parameters w.r.t number of the client, number of samples, and size of objects. 

				$ ./run_s3benchmark.sh -nc 32,64,128 -ns 1024,2048,4096 -s 1Mb,4Mb,128Mb  

				Note: It will generate a list of JSON files for each iteration as well as log file inside the "s3bench_basic/benchmark.log" directory. 

	   ii). To generate a report, please run below command: 

				$ python3 s3benchReport.py benchmark.log
				
	5. Steps to run hsbench wrapper scripts
			
		$ cd allbenchmark/hsbench;
		
		i). Similarly, for hsbench, the User can use additional parameters to test S3 performance like Number of buckets, Number of Objects, size of objects, Number of clients/Threads, and also runtime (Duration). 

				$ ./run_benchmark.sh -b 8,16,32,64 -o 1024,2048 -s 1Mb,4Mb,16Mb,32Mb -t 32,48,64,96,128 -d 600 

				Note: It will generate a list of JSON files for each iteration as well as log file inside the "hsbench/benchmark.log" directory. 

	   ii). To generate a report, please run below command: 

				$ Python3 hsbenchReport.py benchmark.log
		
	6. steps to Intall and configure cosbench
	
	    $ tar -xzvf BENCHMARK.tar.gz 

        $ cd allbenchmark/cosbench 
        
        i) Create a file "driver-nodes-list" where you have to list out clients fqdn like below: 
        
			S3CLIENT1.colo.seagate.com       
			S3CLIENT2.colo.seagate.com 
        
       ii) Installing cosbench on controller and driver nodes: 
        
			$ sh cosbench.sh install --controller <CLIENT1-FQDN> --drivers driver-nodes-list 
                
       iv) Configuring cosbench 
        
			$ sh cosbench.sh configure --controller <CLIENT1-FQDN> --drivers driver-nodes-list 
        
        v) Starting cosbench on controller and driver nodes 
        
			$ sh cosbench.sh start --controller <CLIENT1-FQDN> --drivers driver-nodes-list 
        
       vi) Now you can run cosbench wrapper script like below: 
        
			Ex: ./s3cosbench_benchmark.sh -nc 8,16,32 -ns 1024,2048,4096 -s 1Mb,4Mb,16Mb -b 8,16,32 -w read -t 600 
        
      vii) To Stop cosbench service on controller and driver nodes  
        
			$ sh cosbench.sh stop --controller <CLIENT1-FQDN> --drivers driver-nodes-list 
