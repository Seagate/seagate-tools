grep -w PutObject s3server-0x7200000000000001\:0x*/s3server.INFO > beforeP
grep -w GetObject s3server-0x7200000000000001\:0x*/s3server.INFO > beforeG
grep -w DeleteObject s3server-0x7200000000000001\:0x*/s3server.INFO > beforeD
grep -w PutObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > beforePT
grep -w GetObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > beforeGT
grep -w DeleteObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > beforeDT
