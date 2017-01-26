from pyzabbix import ZabbixAPI
import sys

zapi = ZabbixAPI("http://zabbix.ustack.com")
zapi.login("wentian", "65107318")
print "Connected to Zabbix API Version %s" % zapi.api_version()


def get_proxy_id(region, num="0", server_num="247"):
    proxy_name = "server-%s.%s.%s.ustack.in" % (server_num, num, region)
    proxys = zapi.proxy.get(search={"host": proxy_name}) 
    if len(proxys) > 0:
         return proxys[0]['proxyid']
    raise Exception("There is no proxy named %s" % proxy_name)

def get_template_id(template_name):
    search = {"host": template_name}
    templates = zapi.template.get(search=search) 
    if len(templates) > 0:
        return {"templateid": templates[0]['templateid']}
    raise Exception("There is no template named %s" % template_name)

def get_hostgroup_id(hostgroup_name):
    search = {"name": hostgroup_name}
    hostgroups = zapi.hostgroup.get(search=search) 
    if len(hostgroups) > 0:
         return hostgroups[0]['groupid'] 
    raise Exception("There is no hostgroup named %s" % hostgroup_name)

def get_configuration():
    physical_hostgroup_id = get_hostgroup_id("Type [Physical Machine]") 
    virtual_hostgroup_id = get_hostgroup_id("Type [Virtual Machine]")
    system_information = get_template_id("System Information Template")
    system_load = get_template_id("System Load Template")
    ceph_monitor = get_template_id("Template Ceph Monitor")
    hardware = get_template_id("Template Hardware")
    nova_compute = get_template_id("Template Nova Compute")
    virtual_interface = get_template_id("Template Virtual Interface")
    l4 = get_template_id("Template L4")
    l7 = get_template_id("Template L7")
    applogmon = get_template_id("Template App Logmon")
    memcached = get_template_id("Template Memcached")
    rabbitmq = get_template_id("Template App RabbitMQ")
    mysql = get_template_id("Template MySQL")
    network = get_template_id("Template Network")
    public_network = get_template_id("User Public Network")
    ssdb = get_template_id("Template App SSDB")
    web = get_template_id("Template Web")
    portal_public_network = get_template_id("Portal Public Network")
    zabbix_proxy = get_template_id("Template App Zabbix Proxy")
    configuration = { 
        "Ceph Monitor": {
          "ip_range": "61-63",
          "templates": [system_information, system_load, ceph_monitor],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Compute": {
          "ip_range": "68-232",
          "templates": [system_information, system_load, hardware, nova_compute, virtual_interface],
          "hostgroups": [physical_hostgroup_id]
        },
        "Hypervisor": {
          "ip_range": "233-236",
          "templates": [system_information, system_load, hardware, portal_public_network],
          "hostgroups": [physical_hostgroup_id]
        },
        "L4": {
          "ip_range": "35-38",
          "templates": [system_information, system_load, l4],
          "hostgroups": [virtual_hostgroup_id]
        },
        "L7": {
          "ip_range": "31-34",
          "templates": [system_information, system_load, l7],
          "hostgroups": [virtual_hostgroup_id]
        },
        "MQ": {
          "ip_range": "44-46",
          "templates": [system_information, system_load, rabbitmq],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Memcached": {
          "ip_range": "47-48",
          "templates": [system_information, system_load, memcached],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Monitor": {
          "ip_range": "247-248",
          "templates": [system_information, system_load, zabbix_proxy],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Mysql": {
          "ip_range": "49-50",
          "templates": [system_information, system_load, mysql],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Network": {
          "ip_range": "64-67",
          "templates": [system_information, system_load, network],
          "hostgroups": [physical_hostgroup_id]
        },
        "SSDB": {
          "ip_range": "53-60",
          "templates": [system_information, system_load, ssdb],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Web": {
          "ip_range": "39-43",
          "templates": [system_information, system_load, web],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Image": {
          "ip_range": "241",
          "templates": [system_information, system_load],
          "hostgroups": [virtual_hostgroup_id]
        },
        "Doctor": {
          "ip_range": "242",
          "templates": [system_information, system_load],
          "hostgroups": [virtual_hostgroup_id]
        }
    }
    return configuration

configuration = get_configuration() 

def create_discovery_action(region_name, role, prefix): 
    action_name = "Auto Discovery %s %s" % (region_name, role)
    esc_period = 0 
    # make sure discovery action
    eventsource=1
    # is enable 0 is enable
    status=0
    # AND and Or
    evaltype=0 
    # Conditions
    condition_proxy = {
       "conditiontype": 20,
       "value": get_proxy_id(region_name.split()[0].lower()) 
    }
    condition_status = {
       "conditiontype": 10,
       "value": 0 
    }
    condition_discovery_type = {
       "conditiontype": 8,
       "value": 9 
    }
    condition_host_ip = {
       "conditiontype": 7,
       "value": prefix + configuration[role]['ip_range']
    }
    conditions=[condition_proxy, condition_status, condition_discovery_type, condition_host_ip]
    operation_add_host = {
         "esc_step_from": 1,
         "esc_period": 0,
         "esc_step_to": 1,
         "operationtype": 2
    }
    print configuration[role]
    operation_add_to_hostgroup = {
         "esc_step_from": 1,
         "esc_period": 0,
         "esc_step_to": 1,
         "operationtype": 4,
         "opgroup":[
             {"groupid": get_hostgroup_id("Role [%s]" % role)}, 
             {"groupid": get_hostgroup_id("Region [%s]" % region_name)}, 
             {"groupid": configuration[role]['hostgroups'][0]}
         ]
    }
    operation_link_to_template = {
         "esc_step_from": 1,
         "esc_period": 0,
         "esc_step_to": 1,
         "operationtype": 6,
         "optemplate": configuration[role]['templates']
    }
    # Operations
    operations=[operation_add_host, operation_add_to_hostgroup, operation_link_to_template]
    return zapi.action.create(name=action_name, conditions=conditions, operations=operations, eventsource=1, esc_period=60, evaltype=1)

if __name__ == "__main__":  
    #print zapi.hostgroup.create("Region [%s]" % sys.argv[1])
    #print zapi.drule.create(name="", iprange=sys.argv[2]+"31-255")
    #print zapi.drule.create(name="", iprange=sys.argv[2]+"1-30")
    for conf in configuration:
        create_discovery_action(sys.argv[1], conf, sys.argv[2])
