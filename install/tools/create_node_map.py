#!/usr/bin/env python

import yaml

def get_config(config_path):
    config = yaml.safe_load(file(config_path))
    return config

def create_host_var(mac_map):
    for host in mac_map:
        for ip, mac in host.items():
            host_file = open('/root/ctask/inventory/host_vars/%s' % ip, 'w')
            content = "asset_sn: SMC0025903EF5CE \nnode_mac: %s\n" % mac
            host_file.write(content)
            host_file.close()

def create_inventory(node_map, domain):
    inventory_file = open('/root/ctask/inventory/%s' % domain, 'w')
    inventory_file.truncate()
    inventory_file.close()
    inventory_file = open('/root/ctask/inventory/%s' % domain, 'a')
    common = "[%s:children]\n" % domain
    for node_role in node_map:
        for role, ips in node_role.items():
            content = "[%s]\n" % role
            common = common + role + "\n"
            for ip in ips:
                content =  content + ip + "\n" 
            content =  content + "\n" 
            inventory_file.write(content)
    inventory_file.write(common)
    inventory_file.close()


if __name__ == '__main__':
   config = get_config('/root/ctask/install/config.yaml')
   create_host_var(config['mac_map'])
   create_inventory(config['node_map'], config['domain'])
