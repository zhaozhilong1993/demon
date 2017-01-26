#!/usr/bin/python

from keystoneclient.auth.identity import v2
from keystoneclient import session
from novaclient.client import Client
import sys

AUTH_URL="http://l7.0.shzh.ustack.in:35357/v2.0/"
USERNAME="admin"
PASSWORD="PASSWORD"
PROJECT_ID="admin"

flavor_data = {
   "micro-1": {
       "ram": 512,
       "vcpu": 1
   },
   "micro-2":
   {
       "ram": 1024,
       "vcpu": 1
   },
   "standard-1":
   {
       "ram": 2048,
       "vcpu": 1
   },
   "stardard-2":
   {
       "ram": 4096,
       "vcpu": 2
   },
   "standard-4":
   {
       "ram": 8192,
       "vcpu": 4
   },
   "standard-8":
   {
       "ram": 16384,
       "vcpu": 8
   },
   "standard-12":
   {
       "ram": 24576,
       "vcpu": 12
   },
   "standard-16":
   {
       "ram": 32768,
       "vcpu": 16
   },
   "memory-1":
   {
       "ram": 4096,
       "vcpu": 1
   },
   "memory-2":
   {
       "ram": 8196,
       "vcpu": 2
   },
   "memory-4":
   {
       "ram": 16384,
       "vcpu": 4
   },
   "memory-8":
   {
       "ram": 32768,
       "vcpu": 8
   },
   "memory-12":
   {
       "ram": 49152,
       "vcpu": 16
   },
   "compute-2":
   {
       "ram": 2048,
       "vcpu": 2
   },
   "compute-4":
   {
       "ram": 4096,
       "vcpu": 4
   },
   "compute-8":
   {
       "ram": 8192,
       "vcpu": 8
   },
   "compute-12":
   {
       "ram": 12288,
       "vcpu": 12
   }
}

def get_nova_client():
    novacli = Client("2", USERNAME, PASSWORD, PROJECT_ID, AUTH_URL)
    return novacli

if __name__ == "__main__":
    novacli = get_nova_client()
    for data in flavor_data:
        is_equal = False
        flavors = novacli.flavors.list()
        for flavor in flavors:
            if data == flavor.name:
                is_equal = True
        if not is_equal:
            print novacli.flavors.create(data, flavor_data[data]['ram'], flavor_data[data]['vcpu'], 20)
