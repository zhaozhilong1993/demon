#!/bin/bash

DISKS=`ls /sys/block/ | grep sd`
IS_SSD=0
SYSTEM_DISK=`lsblk | awk '{print $1}' | awk 'BEGIN { current=""; systemd="" } /^sd*/ {current=$NF} /ustack_pv-rootvol$/ {systemd=current} END {print systemd}'`

IS_SSD=`cat /sys/block/$SYSTEM_DISK/queue/rotational`
SIZE=`cat /sys/block/$SYSTEM_DISK/size`
F_SIZE=$[$SIZE*512/1024/1024/1024]
if [[ $IS_SSD == 0 && $F_SIZE -gt 400 && $F_SIZE -lt 600 ]]
then
    echo "ERROR"
elif [[ $F_SIZE -gt 700 && $F_SIZE -lt 1600 ]]
then
    echo "ERROR"
elif [[ $IS_SSD == 1 && $F_SIZE -gt 3500 ]]
then
    echo "ERROR"
else
    echo "OK"
fi
