#!/usr/bin/env python

import optparse
import sys
import json
import requests

headers = {'content-type': 'application/json'}

def generate_options():
    p = optparse.OptionParser()
    p.add_option("--method", "-m")
    p.add_option("--name", "-n")
    p.add_option("--model", "-o")
    p.add_option("--mac", "-k")
    p.add_option("--sn", "-s")
    p.add_option("--nodeid", "-d")
    p.add_option("--ip", "-i")
    p.add_option("--region", "-r")
    p.add_option("--cluster_id", "-l")
    p.add_option("--classify", "-c")
    p.add_option("--channel", "-a")
    p.add_option("--role", "-e")
    options, argument = p.parse_args()
    return options

def get_client(resource, method="GET", data=None):
    """ client for cmdb

    :resource: asset or node or others
    :data: data to post 
    :returns: return data 

    """
    url = "http://cmdb.ustack.com:8080/v1/"
    finalurl = url + resource
    if method == "GET":
        r = requests.get(finalurl, params=data)
        return r.json()
    elif method == "POST":
        r = requests.post(finalurl, data=json.dumps(data), headers=headers)
        return r.json()

def main():
    options = generate_options() 
    if options.method == "check_asset":
        assets = get_client("assets", method="GET", data={"asset_sn": options.sn})
        if len(assets) > 0:
            print "Exist" 
        else:
            print "Not Exist"
    elif options.method == "get_asset":
        print get_client("assets", method="GET", data={"asset_sn": options.sn})[0]['id']
    elif options.method == "find_asset_by_sn":
        assets = get_client("assets", method="GET", data={"asset_sn": options.sn})
        print assets[0]['id']
    elif options.method == "create_asset":
        regions = get_client("regions", method="GET", data={"region_name": options.region})
        channels = get_client("channels", method="GET", data={"channel_name": options.channel})
        models = get_client("models", method="GET", data={"model_name": options.model})
        asset_data = {
                "asset_model": models[0]['id'],
                "asset_sn": options.sn,
                "asset_channel": channels[0]['id'],
                "asset_order_num": "xxx",
                "asset_invoice_num": "xxx",
                "asset_occasion": "2013-08-12",
                "asset_over_protection_date": "2013-08-12",
                "asset_classify": "node",
                "asset_extend_value": "",
                "asset_area": 3,
                "asset_region": regions[0]['id'],
                "asset_department": 1
        }
        print get_client("assets", method="POST", data=asset_data)
    elif options.method == "check_node":
        nodes = get_client("nodes", method="GET", data={"node_ip": options.ip})
        if len(nodes) > 0:
            print "Exist"
        else:
            print "Not Exist"
    elif options.method == "create_node":
        domain = ".ustack.in"
        cluster_id = options.cluster_id
        region_small = options.region.lower()
        last_num = options.ip.split(".")[3]
        server_name = "server-" + last_num + "." + cluster_id + "." + region_small + domain
        node_data = {
                "id": options.nodeid,
                "node_name": server_name, 
                "node_link": server_name,
                "node_role": options.role,
                "node_ip": options.ip,
                "node_mac": options.mac,
                "node_subnet": region_small + "-" + cluster_id,
                "node_type": "server",
                "node_ptale": "CentOSSinglePhysical",
                "node_media": region_small + "-" + cluster_id,
        }
        get_client("nodes", method="POST", data=node_data)
    elif options.method == "find_region_id":
        regions = get_client("regions", method="GET", data={"region_name": options.name})
        print regions[0]['id']
    elif options.method == "find_channel_id":
        channels = get_client("channels", method="GET", data={"channel_name": options.name})
        print channels[0]['id']
    elif options.method == "find_model_id":
        models = get_client("models", method="GET", data={"model_name": options.name})
        print models[0]['id']

if __name__ == '__main__':
    main()
