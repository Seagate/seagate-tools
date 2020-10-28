# Ref - https://github.com/Seagate/cortx-prvsnr/wiki/Deploy-Stack#manual-fix-in-case-the-node-has-been-reimaged

# Remove volume_groups, if present
swapoff -a
for vggroup in $(vgdisplay | grep vg_metadata_srvnode-|tr -s ' '|cut -d' ' -f 4); do
    echo "Removing volume group ${vggroup}"
    vgremove --force ${vggroup}
done

# Remove partitions from volumes
partprobe
for partition in $( ls -1 /dev/disk/by-id/scsi-*|grep part1|cut -d- -f3 ); do
    if parted /dev/disk/by-id/scsi-${partition} print; then 
        echo "Removing partition 2 from /dev/disk/by-id/scsi-${partition}"
        parted /dev/disk/by-id/scsi-${partition} rm 2
        echo "Removing partition 1 from /dev/disk/by-id/scsi-${partition}"
        parted /dev/disk/by-id/scsi-${partition} rm 1
    fi
done
partprobe

shutdown -r now