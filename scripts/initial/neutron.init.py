#!/usr/bin/python

from keystoneclient.auth.identity import v2
from keystoneclient import session
from neutronclient.v2_0 import client
import sys

PUBLIC_NET_NAME="CHINATELECOM"
PUBLIC_SUBNET_NAME="CHINATELECOM"
PUBLIC_SUBNET_CIDR="115.238.155.160/27"
SHARED_SUBNET_CIDR="172.30.248.0/22"
START="115.238.155.162"
END="115.238.155.190"
DNS="1.2.4.8 114.114.114.114"
VLAN_ID="2001"

AUTH_URL="http://l7.0.shzh.ustack.in:35357/v2.0/"
USERNAME="admin"
PASSWORD="PASSWORD"
PROJECT_ID="admin"

def get_neutron_client():
    neutroncli = client.Client(username=USERNAME, password=PASSWORD, tenant_name=PROJECT_ID, auth_url=AUTH_URL)
    return neutroncli

def check_neutron_external_network(neutroncli):
    networks = neutroncli.list_networks()['networks']
    for network in networks:
        if network['name'] == PUBLIC_NET_NAME:
            return True
    return False

def create_neutron_external_network(neutroncli):
    body = {
      "network": {
        "name": PUBLIC_NET_NAME,
        "provider:network_type": "local",
        "router:external": True
       }
    }
    return neutroncli.create_network(body)

def create_neutron_shared_network(neutroncli):
    body = {
      "network": {
        "name": "shared",
        "provider:network_type": "vlan",
        "provider:segmentation_id": VLAN_ID,
        "provider:physical_network": "physnet3",
        "shared": True,
        "uos:rate_limit": 1000
      }
    }
    return neutroncli.create_network(body)

def check_neutron_shared_network(neutroncli):
    networks = neutroncli.list_networks()['networks']
    for network in networks:
        if network['name'] == "shared":
            return True
    return False

def get_neutron_network_id(neutroncli, network_name=PUBLIC_NET_NAME):
    networks = neutroncli.list_networks()['networks']
    for network in networks:
        if network['name'] == network_name:
            return network['id']
    return None


def create_neutron_subnet(neutroncli, network, name, cidr, enable_dhcp=False, allocation_pool=None, dns_nameservers=None):
    body = {
      "subnet": {
        "name": name,
        "network_id": get_neutron_network_id(neutroncli, network_name=network),
        "enable_dhcp": enable_dhcp,
        "ip_version": 4,
        "cidr": cidr
      }
    }
    if allocation_pool:
        body['subnet']['allocation_pools'] = [allocation_pool]
    if dns_nameservers:
        body['subnet']['dns_nameservers'] = dns_nameservers
    return neutron_client.create_subnet(body)


def check_neutron_subnet(neutroncli, name):
    subnets = neutroncli.list_subnets()['subnets']
    for subnet in subnets:
        if subnet['name'] == name:
            return True
    return False

def create_neutron_router(neutroncli, name):
    body = {
      "router": {
         "name": name,
         "external_gateway_info":{
              "network_id": get_neutron_network_id(neutroncli, network_name="shared")
         }
      }
    }
    return neutron_client.create_router(body)

def check_neutron_router(neutroncli, name):
    routers = neutroncli.list_routers()['routers']
    for router in routers:
        if router['name'] == name:
            return True
    return False

def check_neutron_port(neutroncli, name):
    ports = neutroncli.list_ports()['ports']
    for port in ports:
        if port['name'] == name:
            return True
    return False

def create_neutron_port(neutroncli, name):
    body = {
      "port": {
         "name": name,
         "network_id": get_neutron_network_id(neutroncli, network_name="shared")
      }
    }
    return neutron_client.create_port(body)

def get_port_id_by_name(neutroncli, name):
    for port in neutron_client.list_ports()["ports"]:
        if port['name'] == name:
            return port['id']
    return None

def get_router_id_by_name(neutroncli, name):
    routers = neutroncli.list_routers()['routers']
    for router in routers:
        if router['name'] == name:
            return router['id']
    return None

def add_interface_to_router(neutroncli, router_name, port_name):
    body = {
       "port_id": get_port_id_by_name(neutroncli, port_name)
    }
    return neutron_client.add_interface_router(get_router_id_by_name(neutroncli, router_name), body)


if __name__ == "__main__":
    neutron_client = get_neutron_client()
    if not check_neutron_external_network(neutron_client):
        create_neutron_external_network(neutron_client)
    if not check_neutron_subnet(neutron_client, "ext_shadow_subnet"):
        create_neutron_subnet(neutron_client, PUBLIC_NET_NAME, "ext_shadow_subnet", "240.1.0.0/16")
    if not check_neutron_subnet(neutron_client, PUBLIC_SUBNET_NAME):
        allocation_pool = {
            "start": START,
            "end": END
        }
        create_neutron_subnet(neutron_client, PUBLIC_NET_NAME, PUBLIC_SUBNET_NAME, PUBLIC_SUBNET_CIDR, allocation_pool=allocation_pool)
    if not check_neutron_shared_network(neutron_client):
        create_neutron_shared_network(neutron_client)
    if not check_neutron_subnet(neutron_client, "shared_subnet"):
        DNSS = DNS.split(" ")
        create_neutron_subnet(neutron_client, "shared", "shared_subnet", SHARED_SUBNET_CIDR, enable_dhcp=True, dns_nameservers=DNSS)
    if not check_neutron_router(neutron_client, "shared_router"):
        create_neutron_router(neutron_client, "shared_router")
    if not check_neutron_port(neutron_client, "router_port"):
        create_neutron_port(neutron_client, "router_port")
    try:
        add_interface_to_router(neutron_client, "shared_router", "router_port")
    except:
        pass
