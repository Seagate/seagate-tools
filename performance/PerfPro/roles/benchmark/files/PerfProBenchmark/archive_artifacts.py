import os
import sys
import yaml
conf_yaml = open(sys.argv[1])
parse_conf = yaml.safe_load(conf_yaml)

'''Below configuration parameters are collected from config.yml file'''
nfs_server=parse_conf.get('NFS_SERVER')
nfs_export=parse_conf.get('NFS_EXPORT')
mount_point=parse_conf.get('NFS_MOUNT_POINT')
log_dest=parse_conf.get('NFS_FOLDER')

log_source=sys.argv[2]

class collect_logs:


    def mount_nfs(self):

        """Mounts the NFS export on the mountpoint to copy the collected logs"""

        if str(os.system('mount|grep '+mount_point)) == '0':
            logs.unmount_nfs()
            print('unmounting dedicated perftool mountpoint') 
        os.system('mkdir -p '+mount_point)
        os.system('mount '+nfs_server+':'+nfs_export+' '+mount_point)
        return ('Export mounted')

    def zip_logs(self):

        """Create the Zipped copy of recently collected logs by benchmarking tool"""
       
        os.system(' tar -cvzf '+mount_point+'/'+log_dest+'/'+log_source+'.tar.gz'+' -P '+log_source)
        return('logs collected and zipped as '+log_source+'.tar.gz')
   
    def copy_logs(self):

        """Copy the Zipped copy to NFS Repo"""

        shutil.copy(source_zip_prefix+time_string+'.tar.gz', mount_point+'/'+log_dest)
        return('Logs copied to NFS Repo.')

    def show_logs(self):

        """Show the contents of NFS Repo for verification of code"""

        return(os.listdir(mount_point+'/'+log_dest))
    
    def delete_tarfile(self):

        """Delete tar.gz file from current location"""

        return(os.remove(source_zip_prefix+time_string+'.tar.gz'))

    def unmount_nfs(self):

        """Unmounts the NFS export and deleted the mountpoint"""

        os.system('umount -l '+mount_point)
#        os.system('rmdir '+mount_point)
        return('Exiting after log collection.')

logs=collect_logs()
print(logs.mount_nfs())
print(logs.zip_logs())
#print(logs.copy_logs())
#print(logs.delete_tarfile())
#print(logs.show_logs())
print(logs.unmount_nfs())
