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
        echo "wwn-"`ls -l /dev/disk/by-id/ | grep $disk | grep wwn | grep part2 | awk '{ print $9 }' | cut -d "-" -f2`
    elif [[ $IS_SSD == 1 && $F_SIZE -gt 3500 ]]
    then
        echo "wwn-"`ls -l /dev/disk/by-id/ | grep $disk | grep wwn | grep part2 | awk '{ print $9 }' | cut -d "-" -f2`
    fi
done
