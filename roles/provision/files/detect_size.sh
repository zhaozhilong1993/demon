#!/usr/bin/env python
#coding: utf8
import os,sys

path = '/var/lib/libvirt/images'
if not os.path.ismount(path):
    sys.exit("Disk isn't mount!")
disk = os.statvfs(path)
ssdb_size = int(disk.f_bsize * disk.f_blocks  / 1024 / 1024 / 1024 * 0.4)
print ssdb_size
