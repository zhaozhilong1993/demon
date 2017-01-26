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

if __name__ == '__main__':
   config = get_config('/root/ctask/install/config.yaml')
   create_host_var(config['mac_map'])
