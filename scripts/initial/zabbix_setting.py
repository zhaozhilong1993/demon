#!/usr/bin/env python

import optparse
import sys
from pyzabbix import ZabbixAPI

def generate_options():
    p = optparse.OptionParser()
    p.add_option("--method", "-m", default="group")
    p.add_option("--cluster_id", "-c", default="0")
    p.add_option("--region", "-r", default="TEST")
    p.add_option("--domain", "-d", default="TEST")
    p.add_option("--prefix", "-p", default="10.0.1.")
    p.add_option("--region_user", "-e", default="test")
    p.add_option("--zabbix_user", "-u", default="server-72")
    p.add_option("--zabbix_passwd", "-w", default="ustack")
    options, argument = p.parse_args()
    return options

def create_hostgroup(zapi, region_name, cluster_id):
    """Docstring for create_hostgroup.

    :region_name: region name of hostgroup 
    :returns: create status 

    """
    return zapi.hostgroup.create(name="Region [%s %s]" % (region_name, cluster_id)) 

def check_hostgroup(zapi, region_name, cluster_id):
    """check hostgroup from region name if exists

    :region_name: region name of hostgroup
    :returns: true or false 
    """
    return zapi.hostgroup.exists(name="Region [%s %s]" % (region_name, cluster_id))

def check_zabbixproxy(zapi, domain_name):
    """check domain from domain name if exists

    :domain_name: domain name if this cluster 
    :returns: true or false 

    """
    proxy = zapi.proxy.get(search={"host": "server-247." + domain_name})
    return proxy

def create_zabbixproxy(zapi, domain_name):
    """create zabbix proxy use domain

    :zapi: use to create proxy in zabbix
    :domain_name: domain name of region
    :returns: None

    """
    proxy_host = "server-247." + domain_name
    zapi.proxy.create(host=proxy_host, status=5)

def main():
    options = generate_options() 
    zapi = ZabbixAPI("http://zabbix.ustack.com")
    zapi.login(options.zabbix_user, options.zabbix_passwd)

    if options.method == "create_hostgroup":
        create_hostgroup(zapi, options.region, options.cluster_id)
    elif options.method == "check_hostgroup":
        hostgroup_exists = check_hostgroup(zapi, options.region, options.cluster_id)
        if hostgroup_exists:
            print "Exist" 
        else:
            print "Not Exist" 
    elif options.method == "create_proxy":
        create_zabbixproxy(zapi, options.domain)
    elif options.method == "check_proxy":
        proxy = check_zabbixproxy(zapi, options.domain)
        if len(proxy) > 0:
            print "Exist" 
        else:
            print "Not Exist" 
    elif options.method == "clean_discovery_actions":
        pass
    elif options.method == "create_discovery_actions":
        pass
    elif options.method == "create_region_admin":
        pass
    elif options.method == "remote_region_admin":
        pass

if __name__ == '__main__':
    main()
