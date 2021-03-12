# BENCHMARK
Pre-requisite step to perform AutoPerf s3 performance testing:
1.	It must require root access to the S3 client and S3 server.
2.	Passwordless authentication should be enabled for S3 Client and S3 Server from the AutoPerf server.
3.	All benchmark (s3bench_basic, hsbench, cosbench, and fio) should be configured on both S3 Client and S3 Server.
4.	S3bench executive file should be available inside "~/go/bin/" directories as "s3bench.old". (default name is "s3bench" but it should be "s3bench.old")
5.  Please ensure that hsbench is already available on both S3 Client and S3 Server.
6.	Cosbench is configured and it should be in a working state. All cosbench original files should be residing in "~/cos/" directories. 
 
 
 Note: - 
		1.	While running fio benchmark, you will observe the S3 performance graph (Grafana Dashboard) only on the primary and secondary node of S3 Server respectively. It will not be reflected on your Client server.
		2.	For the remaining benchmark, you can observe the s3 performance graph (Grafana Dashboard) only on the S3 Client server.
