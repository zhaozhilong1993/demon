#!/bin/bash

DISKS=`ls /sys/block/ | grep sd`
IS_SSD=0

for disk in $DISKS
do
    IS_SSD=`cat /sys/block/$disk/queue/rotational`
    SIZE=`cat /sys/block/$disk/size`
    F_SIZE=$[$SIZE*512/1024/1024/1024]
    if [[ $IS_SSD == 0 && $F_SIZE -gt 400 && $F_SIZE -lt 600 ]]
    then
        echo "Compute" 
    elif [[ $F_SIZE -gt 1300 && $F_SIZE -lt 1600 ]]
    then
        echo "RAID 10"
    elif [[ $IS_SSD == 1 && $F_SIZE -gt 3500 ]]
    then
        echo "Ceph"
    else
        echo "System"
    fi
done
