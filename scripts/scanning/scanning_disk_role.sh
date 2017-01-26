#!/bin/bash

DISKS=`ls /sys/block/ | grep sd`
IS_SSD=0
COMPUTE_OSD_NUM=0
CEPH_OSD_NUM=0
SYSTEM_DISK_NUM=0
RAID10_NUM=0

for disk in $DISKS
do
    IS_SSD=`cat /sys/block/$disk/queue/rotational`
    SIZE=`cat /sys/block/$disk/size`
    F_SIZE=$[$SIZE*512/1024/1024/1024]
    if [[ $IS_SSD == 0 && $F_SIZE -gt 400 && $F_SIZE -lt 600 ]]
    then
        COMPUTE_OSD_NUM=`expr $COMPUTE_OSD_NUM + 1`
    elif [[ $F_SIZE -gt 700 && $F_SIZE -lt 1600 ]]
    then
        RAID10_NUM=`expr $RAID10_NUM + 1`
    elif [[ $IS_SSD == 1 && $F_SIZE -gt 3500 ]]
    then
        CEPH_OSD_NUM=`expr $CEPH_OSD_NUM + 1`
    else
        SYSTEM_DISK_NUM=`expr $SYSTEM_DISK_NUM + 1`
    fi
done

if [[ $1 == "Compute" ]]
then
    if [[ $COMPUTE_OSD_NUM == 3 ]]
    then
        echo "OK"
    else
        echo "Problem"
    fi
elif [[ $1 == "Hypervisor" ]]
then
    if [[ $RAID10_NUM == 1 ]]
    then
        echo "OK" 
    else
        echo "Problem"
    fi
else
    echo "OK"
fi
