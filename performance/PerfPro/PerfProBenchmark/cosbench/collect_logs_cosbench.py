PARAMS={
'nfs_server':'cftic2.pun.seagate.com',
'nfs_export':'/cftshare',
'mount_point':'/mnt/benchmark_log_mountpoint/',
'source_zip_prefix':'benchmark_',
'log_source':'benchmark.log/',
'log_dest':'/mnt/benchmark_log_mountpoint/PerfPro/'
}
import os
import shutil
from datetime import datetime as DT
now=DT.now()
time_string = now.strftime("%m-%d-%Y-%H-%M-%S")
os.system('mkdir '+PARAMS['mount_point'])
os.system('mount '+PARAMS['nfs_server']+':'+PARAMS['nfs_export']+' '+PARAMS['mount_point'])
print(PARAMS['nfs_export']+' is mounted on '+PARAMS['mount_point'])
os.system(' tar -cvzf '+PARAMS['source_zip_prefix']+time_string+'.tar.gz'+' '+PARAMS['log_source'])
print('Logs zipped as '+PARAMS['source_zip_prefix']+time_string+'.tar.gz')
shutil.copy(PARAMS['source_zip_prefix']+time_string+'.tar.gz', PARAMS['log_dest'])
print('logs copied to '+PARAMS['nfs_export'])
print('contents of nfs repo\n', os.listdir(PARAMS['log_dest']))
os.system('umount -l '+PARAMS['mount_point'])
print('Export unmounted')
os.system('rmdir '+PARAMS['mount_point'])

