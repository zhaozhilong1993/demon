#!/usr/bin/env python

import argparse
import os
import sys


def generate_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--abridge", help="abridge of region. eg: hx")
    parser.add_argument("-i", "--prefix", help="region id. eg: 10.110.0")
    parser.add_argument("-n", "--name", help="name of region. eg: huaxun")
    parser.add_argument("--enable_sata", help="enable sata",action='store_true')
    parser.add_argument("--enable_uc", help="enable uc",action='store_true')
    options = parser.parse_args()
    return options

def generate_password(length=20):
    Password = ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(length)))[:24]
    return Password

def generate_groups_vars(name,abridge,prefix,sata=None):
        if not os.path.exists('/root/ctask/install/tools/group_vars_template'):
            sys.exit('group_vars_template file is not exist!')
        input = open("/root/ctask/install/tools/group_vars_template")
        lines = input.readlines()
        input.close()
        p = prefix.split('.')
        sdn_prefix = '%s.%s.%d' % (p[0],p[1],int(p[2])+24)
        ceph_prefix = '%s.%s.%d' % (p[0],p[1],int(p[2])+16)
        console_prefix = '%s.%s.%d' % (p[0],p[1],int(p[2])+8)
        cluster_id = '%d' % int(p[2])
        region_domain = '%d.%s.ustack.in' % (int(p[2]),abridge)
        output  = open('/root/ctask/inventory/group_vars/%s' % abridge,'w');
        for line in lines:
            l = line.replace('SDN_PREFIX',sdn_prefix)
            l = l.replace('CEPH_PREFIX',ceph_prefix)
            l = l.replace('CLUSTER_ID',cluster_id)
            l = l.replace('CONSOLE_PREFIX',console_prefix)
            l = l.replace('PREFIX',prefix)
            l = l.replace('REGION_NAME',name)
            l = l.replace('REGION_ABRIDGE',abridge)
            l = l.replace('REGION_DOMAIN',region_domain)
            l = l.replace('RABBIT_PASSWORD',generate_password())
            l = l.replace('MYSQL_ROOT_PASSWORD',generate_password())
            l = l.replace('MYSQL_REP_PASSOWRD',generate_password(10))
            l = l.replace('USER_PASSWORD',generate_password())
            l = l.replace('DB_PASSWORD',generate_password())
            l = l.replace('UOS_PASSWORD',generate_password())
            l = l.replace('KEYSTONE_TOKEN',generate_password())
            l = l.replace('KEYSTONE_ADMIN_PASSWORD',generate_password())
            if sata:
                l = l.replace('ENABLE_SATA','True')
            else:
                l = l.replace('ENABLE_SATA','False')
            output.write(l)
        output.close()

if __name__ == '__main__':
    options = generate_options()
    if options.abridge is None or options.prefix is None or options.name is None:
         sys.exit('ERROR! Please run "python generate_group_vars.py -h"')
    elif len(options.prefix.split('.')) != 3:
         sys.exit('PREFIX is ERROR!')
    if options.enable_uc:
        t_file='uc_inventory_template'
    else:
        t_file='inventory_template_liberty'
    prefix =  options.prefix
    abridge = options.abridge
    name = options.name
    sata = options.enable_sata
    generate_groups_vars(name,abridge,prefix,sata)
    print 'Generate SUCCESS! Please modify the IPMI and IP !'
