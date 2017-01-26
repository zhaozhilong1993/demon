#!/usr/bin/env python

import argparse
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

headers = {'content-type': 'application/json'}

def define_data():
    defined_data = {
            "LB": {
                "cpu": "8",
                "memory": "8589934592",
                "disk": "100G"
            },
            "Web": {
                "cpu": "4",
                "memory": "17179869184",
                "disk": "100G"
            },
            "MQ": {
                "cpu": "8",
                "memory": "8589934592",
                "disk": "100G"
            },
            "Memcached": {
                "cpu": "8",
                "memory": "8589934592",
                "disk": "100G"
            },
            "Mysql": {
                "cpu": "8",
                "memory": "8589934592",
                "disk": "200G"
            },
            "CephMon": {
                "cpu": "8",
                "memory": "8589934592",
                "disk": "100G"
            }
    }
    return defined_data

def generate_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", help="method to do with foreman machine")
    parser.add_argument("-c", "--mac", help="first ethernet mac of the server")
    parser.add_argument("-n", "--name", help="enter the name you want to find")
    parser.add_argument("-d", "--domain", help="set vm domain")
    parser.add_argument("-p", "--prefix", help="prefix of this cluster")
    parser.add_argument("-r", "--region", help="cluster region name")
    parser.add_argument("-g", "--hostgroup", help="host group of in foreman")
    parser.add_argument("-i", "--ip", help="set vm ip")
    parser.add_argument("-o", "--is-online", help="have vpn and have no own UC")
    parser.add_argument("-e", "--enable_public_interface", help="is enable public interface")
    options = parser.parse_args()
    return options


def get_client(resource, method="GET", data=None):
    """ client for cmdb

    :resource: asset or node or others
    :data: data to post
    :returns: return data

    """
    url = "http://foreman.ustack.com:3000/api/v2/"
    basic_auth = HTTPBasicAuth("api_post_user", "n5Ba7Xu2FB")
    finalurl = url + resource
    if method == "GET":
        r = requests.get(finalurl, params=data, auth=basic_auth)
        return r.json()
    elif method == "POST":
        r = requests.post(finalurl, data=json.dumps(data), headers=headers, auth=basic_auth)
        if r.status_code == 200 or r.status_code == 201:
          return r.json()
        else:
          print r.json()
          sys.exit(1)

def search_id_by_name(option, name):
    data = get_client(option, data={"search": name})
    results = data['results']
    if len(results) == 0:
        raise Exception("No %s found" % option)
    return results[0]['id']

def search_by_name(option, name):
    data = get_client(option, data={"search": name})
    results = data['results']
    #if len(results) == 0:
    #    return None
    return results

def search_compute_resource(name):
    data = get_client("compute_resources", data={"search": name})
    #for da in data['results']:
    #    if name == da['name']:
    #        return da['id']
    if len(data['results']) > 0:
        return data
    return None

def create_compute_resource(region, ip):
    nums = ip.split(".")
    data = {
            "compute_resource": {
                "name": "0_%s_hypervisor_%s" % (region, nums[3]),
                "provider": "Libvirt",
                "url": "qemu+ssh://root@%s/system" % ip
            }
    }
    return get_client("compute_resources", "POST", data)


def check_media(domain):
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    return search_id_by_name("media", region + "-" + cluster_id)

def create_media(domain, prefix, is_online):
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    if is_online == 'True':
        IP = '%s31' % prefix
    else:
        IP = '%s30' % prefix
    data = {
        "medium": {
            "name": region + "-" + cluster_id,
            "path": "http://%s:8000/media/$major.$minor" % IP,
            "os_family": "Redhat",
            "operatingsystem_ids": ["1","2"]
        }
    }
    return get_client("media", "POST", data=data)

def create_domain(domain, region):
    data =  {
        "domain": {
            "name": domain,
            "fullname": region
        }
    }
    return get_client("domains", "POST", data=data)

def check_compute_resource(region, ip):
    nums = ip.split(".")
    name = "0_%s_hypervisor_%s" % (region, nums[3])
    return search_compute_resource(name)

def check_domain(domain):
    return search_id_by_name("domains", domain)

def check_smart_proxy(domain):
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    name = region + "-" + cluster_id
    smart_proxies = get_client("smart_proxies", data={"per_page": 500})['results']
    for smart_proxy in smart_proxies:
        if name == smart_proxy['name']:
            return smart_proxy['id']

def create_smart_proxy(domain, prefix, is_online):
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    if is_online == 'True':
        IP = '%s31' % prefix
    else:
        IP = '%s30' % prefix
    data = {
            "name": region + "-" + cluster_id,
            "url": "http://%s:8443" % IP
    }

    return get_client("smart_proxies", "POST", data=data)

def check_subnet(domain):
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    return search_id_by_name("subnets", domain)

def create_subnet(domain, prefix, proxy_id):
    domain_id = check_domain(domain)
    cluster_id = domain.split(".")[0]
    region = domain.split(".")[1]
    name = region + "-" + cluster_id
    data = {
        "subnet": {
            "name": name,
            "network": prefix + "0",
            "mask": "255.255.255.0",
            "dns_primary": "114.114.114.114",
            "gateway": prefix + ".1",
            "domain_ids": [domain_id],
            "dhcp_id": proxy_id,
            "tftp_id": proxy_id
        }
    }
    return get_client("subnets", "POST", data=data)

class VM:
    def __init__(self, ip, region, domain,enable_public_interface,mac='',hostgroup='',server=''):
        defined_data = define_data()
        self.role_decide_num = int(ip.split(".")[3])
        self.fqdn = "server-" + str(self.role_decide_num) + "." + domain
        self.server = server
        self.region = domain.split(".")[1]
        if self.region == "test":
            self.env_id = search_id_by_name("environments", "test")
        if self.region == "dev":
            self.env_id = search_id_by_name("environments", "devel")
        else:
            self.env_id = search_id_by_name("environments", "liberty")

        self.ip = ip
        self.cluster_id = domain.split(".")[0]
        self.ptable_id = search_id_by_name("ptables", 'Kickstart default')
        self.domain_id = search_id_by_name("domains", domain)
        #self.subnet_id = search_id_by_name("subnets", self.region + "-" + self.cluster_id)
        self.subnet_id = search_id_by_name("subnets", 'name=%s-%s' % (self.region,self.cluster_id))
        self.medium_id = search_id_by_name("media", self.region + "-" + self.cluster_id)
        self.operatingsystem_id = search_id_by_name("operatingsystems", 'CentOS 7.1')
        self.hostgroup = hostgroup
        self.hostgroup_id = search_id_by_name("hostgroups", 'name=%s' % self.hostgroup)
        self.interfaces_attributes = {"1":{
                 "type": "Nic::Managed",
                 "identifier": "eth0",
                 "domain_id": self.domain_id,
                 "subnet_id": self.subnet_id,
                 "ip": self.ip,
                 "managed": "1",
                 "primary": "1",
                 "provision": "1",
                 "virtual": "0",
                 "compute_attributes":{
                 "type":"bridge", "bridge":"br0", "model":"virtio"}}
        }
        if self.server == 'real':
            self.interfaces_attributes["1"]['mac']=mac
        if self.server == 'vm':
            self.compute_resource_name = "0_" + region + "_hypervisor_"
            #compute_resources = search_compute_resource(self.compute_resource_name)
            compute_resources = search_by_name("compute_resources", 'name~%s' % self.compute_resource_name)
            compute_resource_num = len(compute_resources)
            hosts = search_by_name("hosts", 'name~.%s.ustack.in and hostgroup=%s' % (self.region, self.hostgroup))
            position =  len(hosts) % compute_resource_num
            self.compute_resource_id = compute_resources[position]['id']
            self.pre_defined_data = defined_data[str(self.hostgroup)]
            self.compute_attributes = {
                    "cpus": self.pre_defined_data['cpu'],
                    "memory": self.pre_defined_data['memory'],
                    "start": '1',
                    "volumes": [
                        {'pool_name': "default", "capacity": self.pre_defined_data['disk']}
                    ]
            }
            if self.hostgroup == "LB" and enable_public_interface == "True":
                self.interfaces_attributes["0"]={
                     "type": "Nic::Managed",
                     "name":"",
                     "domain_id":"",
                     "subnet_id":"",
                     "ip":"",
                     "identifier": "eth1",
                     "managed": "0",
                     "primary": "0",
                     "provision": "0",
                     "virtual": "0",
                     "compute_attributes":{
                     "type":"bridge", "bridge":"br1", "model":"virtio"}
                }

    def _to_json(self):
        if self.server == 'vm':
            vm_data = {
                "host": {
                    "name": self.fqdn,
                    "environment_id": self.env_id,
                    "domain_id": self.domain_id,
                    "operatingsystem_id": self.operatingsystem_id,
                    "hostgroup_id": self.hostgroup_id,
                    "ptable_id": self.ptable_id,
                    "medium_id": self.medium_id,
                    "compute_resource_id": self.compute_resource_id,
                    "build": True,
                    "compute_attributes": self.compute_attributes,
                    "interfaces_attributes": self.interfaces_attributes
                }
            }
        else:
            vm_data = {
                "host": {
                    "name": self.fqdn,
                    "environment_id": self.env_id,
                    "domain_id": self.domain_id,
                    "operatingsystem_id": self.operatingsystem_id,
                    "hostgroup_id": self.hostgroup_id,
                    "ptable_id": self.ptable_id,
                    "medium_id": self.medium_id,
                    "build": True,
                    "interfaces_attributes": self.interfaces_attributes
                }
            }
        return vm_data

    def create_host(self):
        vmdata = self._to_json()
        print vmdata
        return get_client("hosts", "POST", vmdata)


def main():
    options = generate_options()
    if options.method == "check_host":
        try:
            search_id_by_name("hosts", options.ip)
            print "Exist"
        except Exception, e:
            print "Not Exist"
    elif options.method == "create_host":
        if len(options.ip.split(".")) != 4:
            raise Exception("IP Was in incorrect format")
        else:
            vm = VM(options.ip, options.region ,options.domain, options.enable_public_interface,'', options.hostgroup,'vm')
            print vm.create_host()
    elif options.method == "create_server":
        if len(options.ip.split(".")) != 4:
            raise Exception("IP Was in incorrect format")
        else:
            vm = VM(options.ip, options.region,  options.domain, options.enable_public_interface,options.mac,options.hostgroup,'real')
            print vm.create_host()
    elif options.method == "check_subnet":
        try:
            check_subnet(options.domain)
            print "Exist"
        except Exception, e:
            print "Not Exist"
    elif options.method == "create_subnet":
        proxy_id = check_smart_proxy(options.domain)
        print create_subnet(options.domain, options.prefix, proxy_id)
    elif options.method == "check_domain":
        try:
            check_domain(options.domain)
            print "Exist"
        except Exception, e:
            print "Not Exist"
    elif options.method == "check_media":
        try:
            check_media(options.domain)
            print "Exist"
        except Exception, e:
            print "Not Exist"
    elif options.method == "create_media":
        print create_media(options.domain, options.prefix, options.is_online)
    elif options.method == "check_smart_proxy":
        try:
            is_smart_proxy = check_smart_proxy(options.domain)
            if is_smart_proxy:
                print "Exist"
            else:
                print "Not Exist"
        except Exception, e:
            print "Not Exist"
    elif options.method == "create_smart_proxy":
        print create_smart_proxy(options.domain, options.prefix, options.is_online)
    elif options.method == "create_domain":
        print create_domain(options.domain, options.region)
    elif options.method == "check_compute_resource":
        compute_resource = check_compute_resource(options.region, options.ip)
        if compute_resource == None:
            print "Not Exist"
        else:
            print "Exist"
    elif options.method == "create_compute_resource":
        print create_compute_resource(options.region, options.ip)

if __name__ == '__main__':
    main()
