object = 32
grep -w PutObject s3server-0x7200000000000001\:0x*/s3server.INFO > afterP_$object
grep -w GetObject s3server-0x7200000000000001\:0x*/s3server.INFO > afterG_$object
grep -w DeleteObject s3server-0x7200000000000001\:0x*/s3server.INFO > afterD_$object
grep -w PutObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > afterPT_$object
grep -w GetObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > afterGT_$object
grep -w DeleteObjectTagging s3server-0x7200000000000001\:0x*/s3server.INFO > afterDT_$object
