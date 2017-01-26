#!/bin/bash
#  维护人员: xingchao@unitedstack.com
set -x

which facter > /dev/null || yum install -y puppet
which parted > /dev/null || yum install -y parted

export LANG='en_US.UTF-8'

virtual=`facter is_virtual`
blockdevices=`facter blockdevices`
origin_disk_list=${blockdevices//,/ }
is_softraid=$(cat /proc/mdstat |  awk -F':' '/Personalities/ {print $2}'|grep -i raid >/dev/null; echo $?)
systemdiskpart=`df -h |grep 'boot'|awk {'print $1'}|cut -d/ -f3`
if [[ $virtual == true ]]; then
  # systemdisk of virtual-machine
  systemdisk=vda
else
  systemdisk=${systemdiskpart:0:3}
fi
disk_list=`echo $origin_disk_list | sed "s/$systemdisk//g" | sed "s/sr0//g"`
journal_size=15
disk_type=${DISK_TYPE:-'ssd'}
filename=`hostname`
node_type=${NODE_TYPE:-'storage'}

echo "$filename is initialing OSD now..."
[ -f /tmp/wwn ] && rm -f /tmp/wwn

case $node_type in
    compute)
        roles='compute'
       ;;
    storage)
        roles='storage::ceph::osd'
        ;;
    *)
      echo "don't found this node type $node_type"
      exit 1
      ;;
esac

# 如果需要在每个服务器上添加一些定制化参数，请编辑以下代码
if [[ "$disk_type" == 'sata' ]]; then
    echo -ne "sunfire::${roles}::enable_osd: true
sunfire::${roles}::osd_disk_type: 'sata'
sunfire::${roles}::osd_dict:
" > /tmp/${filename}.yaml
elif [[ "$disk_type" == 'ssd' ]]; then
    echo -ne "sunfire::${roles}::enable_osd: true
sunfire::${roles}::osd_disk_type: 'ssd'
sunfire::${roles}::osd_dict:
" > /tmp/${filename}.yaml
else
    echo "disk type $disk_type is wrong!" && exit 1
fi

# Collect WWN info
for i in $disk_list
do
  is_virtual=`facter |grep is_virtual |awk '{print $3}'`
  if [[ $is_virtual == false ]]; then
    wwn=`ls -al /dev/disk/by-id/ |grep $i |awk {'print $9'} |egrep '^wwn*'|grep -v part`
    [[ `echo $wwn |wc -w` == 1 ]] || (echo '$wwn is invalid' && exit 1)
    echo "  ${wwn}-part2: ${wwn}-part1" >> /tmp/${filename}.yaml
  else
    virtio=`ls -al /dev/disk/by-id/ |grep $i |awk {'print $9'} |egrep '^virtio*'|grep -v part`
    [[ `echo $virtio |wc -w` == 1 ]] || (echo '$virtio is invalid' && exit 1)
    echo "  ${virtio}-part2: ${virtio}-part1" >> /tmp/${filename}.yaml
  fi
done

# Remove original partition, erase data and part again
if [[ $is_softraid -eq 0 ]]; then
   echo "SoftRAID detected, please format it manually !"
   exit 1
else
    for i in $disk_list
    do
      mount|grep $i && echo "$i is mounted" && continue
      partition_list=`parted -a optimal -s /dev/$i print|grep -Ev '错误|Error'|tail -n3|awk '{print $1}'`

      for p in $partition_list
      do
        if [[ "$p" =~ [0-9] ]]
        then
            parted -a optimal -s /dev/$i rm $p
        else
           echo 'No exist partition or sth wrong.'
        fi
      done
      dd if=/dev/zero of=/dev/$i bs=16k count=12800 || echo 'dd operaion failed'

      parted -a optimal -s /dev/$i mktable gpt
      parted -a optimal -s /dev/$i mkpart ceph 0% ${journal_size}GB
      parted -a optimal -s /dev/$i mkpart ceph ${journal_size}GB 100%
    done
fi


echo "$filename OSD Initial Task is Done."

cat /tmp/${filename}.yaml
