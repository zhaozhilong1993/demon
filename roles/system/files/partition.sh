#!/bin/bash

SYSTEM_DISK=`df -Th | awk -F'[/ 1]' '{if($NF=="boot")print $3}'`
DISK_LISTS=`ls /dev/sd*| grep -E 'sd.$' | cut -d / -f 3 | sed "s/$SYSTEM_DISK//g"`

# Compute OSD
for d in $DISK_LISTS
do
    part_num=`ls -al /dev/disk/by-id/ | grep $d | grep wwn* | grep part | wc -l`
    if [[ $part_num == 0 ]];then
sudo sfdisk /dev/$d << EOF 
1 - - *;
EOF
mkfs.ext4 /dev/$d'1'
    else
        echo "Disk Partition Already Exists"
    fi
done
