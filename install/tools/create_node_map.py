#!/usr/bin/env python

import yaml

def get_config(config_path):
    config = yaml.safe_load(file(config_path))
    return config

def create_host_var(mac_map):
    for host, info in mac_map.items():
        host_file = open('/root/ctask/inventory/host_vars/%s' % host, 'w')
        content = "asset_sn: SMC0025903EF5CE\n" 
        for key, value in info.items():
            content = content + key + ': ' + value + '\n'
        host_file.write(content)
        host_file.close()

def create_inventory(node_map, domain):
    inventory_file = open('/root/ctask/inventory/%s' % domain, 'w')
    inventory_file.truncate()
    inventory_file.close()
    inventory_file = open('/root/ctask/inventory/%s' % domain, 'a')
    common = "[%s:children]\n" % domain
    for node_role, ips in node_map.items():
        content = "[%s]\n" % node_role
        common = common + node_role + "\n"
        for ip in ips:
            content =  content + ip + "\n" 
        content =  content + "\n" 
        inventory_file.write(content)
    inventory_file.write(common)
    inventory_file.close()

def create_ceph_info(config):
    members = config['node_map']['CephMonitor']
    content = '\nceph_mon_hosts: '
    ips = ''
    for ip in members:
        if ips:
            ips = ips + ',' + ip
        else :
            ips = ips + ip
    content = content + ips
    config_file = open('/root/ctask/install/config.yaml', 'a')
    config_file.write(content)
    config_file.close()


if __name__ == '__main__':
   config = get_config('/root/ctask/install/config.yaml')
   create_host_var(config['ip_info_map'])
   create_inventory(config['node_map'], config['domain'])
   create_ceph_info(config)
