#!/usr/bin/python

from pyzabbix import ZabbixAPI
import sys

username="wentian"
password="65107318"

zapi = ZabbixAPI("http://zabbix.ustack.com")
zapi.login(username, password)
print "Connected To Zabbix API Version %s" % zapi.api_version() 
hostgroup_id = sys.argv[1]
status = int(sys.argv[2])


def get_hostgroup_id(hostgroup_name):
    search = {"name": hostgroup_name}
    hostgroups = zapi.hostgroup.get(search=search)
    if len(hostgroups) > 0:
        return hostgroups[0]['groupid']

def get_hosts(groupid):
    groupids = [groupid]
    hosts = zapi.host.get(groupids=groupids)
    return hosts

def update_machine_set_status(hosts, status=0):
    result_hosts = []
    for host in hosts:
        result_hosts.append({"hostid": host["hostid"]})
    zapi.host.massupdate(hosts=result_hosts, status=status)

if __name__ == "__main__":
    hosts = get_hosts(get_hostgroup_id(hostgroup_id))
    update_machine_set_status(hosts, status)
