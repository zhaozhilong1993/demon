#!/bin/bash

SYSTEM_DISK=`df -Th | awk -F'[/ 1]' '{if($NF=="boot")print $3}'`
DISK_NUMBERS=`ls /dev/sd*| grep -E 'sd.$' | cut -d / -f 3 | sed "/$SYSTEM_DISK/d"| wc -l`

if [ $DISK_NUMBERS -eq 1 ];then
    DISK=`ls /dev/sd*| grep -E 'sd.$' | cut -d / -f 3 | sed "/$SYSTEM_DISK/d"`
    echo $DISK"1"
else
    echo "$DISK_NUMBERS disks found!"
    exit 1
fi
