#!/usr/bin/env python
# encoding: utf-8

#    Copyright (C) 2015 UnitedStack All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
#    Author: wentian
#    Email: wentian@unitedstack.com
#
#    标题：一个Excel和CMDB以及Ansible的转换工具
#   
#    用法：
#    
#    check_sheet:
#       parameters
#          - file   输入的Excel文件
#       todo
#          - excel格式校验
#    asset_generate: 
#       parameters
#          - file   输入的Excel文件 
#       todo
#          - 自动生成Asset, 校验是否已经存在
#    info_generate: 
#       parameters
#          - prefix Region的前一半IP如10.1.0.
#          - tagexcel  最后输出的Excel
#          - hostvars  用于生成HostVar的数据目录
#
import xlrd
import xlwt
import requests
import os
import json
import argparse

role_map = {
        "Network": "64-67",
        "Compute": "68-200",
        "Hyper": "233-236",
        "Storage": "201-232"
}

worksheet_name = u"服务器硬盘信息"

headers = {'content-type': 'application/json'}

def get_worksheet(filename):
    workbook = xlrd.open_workbook(filename)
    worksheet_name = workbook.sheet_names()[0]
    worksheet = workbook.sheet_by_name(worksheet_name)
    return worksheet

def generate_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method", help="选择要使用的方法[1. check_sheet （表格语法检测）2.asset_generate （生成资产信息）3. info_generate（生成Excel信息和Ansible信息）")
    parser.add_argument("-f", "--file", help="filepath of node info")
    parser.add_argument("-p", "--prefix", help="prefix of the region")
    parser.add_argument("-r", "--region", help="Region名称")
    parser.add_argument("-t", "--tagexcel", help="用于生成标签Excel")
    parser.add_argument("-o", "--hostvars", help="用于生成HostVar的数据目录")
    parser.add_argument("-c", "--computestart", help="Compute 开始的编号 (仅用于扩容，初始化时不需要传)", default=68)
    parser.add_argument("-n", "--networkstart", help="Network 开始的编号（仅用于扩容，初始化时不需要传）", default=64)
    parser.add_argument("-y", "--hyperstart", help="Hyper 开始的编号 （仅用于扩容，初始化时不需要传）", default=233)
    options = parser.parse_args()
    return options

def write_files(racks_info):
    for rack_key in racks_info:
        rack_machines = racks_info[rack_key]
        for machine_key in rack_machines:
            machine = rack_machines[machine_key]['info']
            filename = options.hostvars + machine['ip'] 
            if not os.path.exists(filename):
                filehandler = open(filename, 'w')
                filehandler.write("# file: host_var/%s\n\nasset_sn: %s\nnode_mac: %s" % (machine['ip'], machine['sn'], machine['mac']))
            else:
                print "File %s exists" % filename

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

def is_rack_line(column_types):
    zero_num = 0
    for i in range(1,4):
        if column_types[i] == 0:
            zero_num += 1
    if zero_num == 3:
        return True
    else:
        return False

def replace_disk(disk):
    disk = disk.replace(u"硬盘", "")
    disk = disk.replace(u"（", "")
    disk = disk.replace(u"）", "")
    disk = disk.replace(u"SAS", "")
    disk = disk.replace(u"SATA", "")
    disk = disk.replace(u"SSD", "")
    disk = disk.replace(u"，", "")
    disk = disk.replace(u"数据盘", "")
    disk = disk.replace(u"系统盘", "")
    disk = disk.replace(u" ", "")
    return disk

def judge_disks(type ,disk):
    if disk != "" and u"硬盘" in type:
        return disk
    else:
        return None

def get_node_info_from_worksheet(worksheet):
    racks = {}
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = -1
    node_info = [] 

    racks = {}

    node_line = 0
    cached_disk = {} 
    rack_now = ""
    server_now = ""

    while curr_row < num_rows:
        curr_row += 1
        column_types = []
        column_values = []
        for i in range(0,4):
            column_types.append(worksheet.cell_type(curr_row, i))
            column_values.append(worksheet.cell_value(curr_row, i))
        if is_rack_line(column_types):
            rack_now = column_values[0]
            racks[rack_now] = {} 
        else:
            if column_values[0] == u"服务器型号":
                node_line += 1
                #cached_disk[num5] = judge_disks(column_values[5], column_values[6])
                #cached_disk[num7] = judge_disks(column_values[7], column_values[8])
            elif node_line >= 1:
                node_line -= 1
                server_now = str(column_values[1])
                racks[rack_now][server_now] = {
                        "info": {
                            "model": column_values[0].replace(" ", ""),
                            "sn": str(column_values[1]).split(".")[0].replace(" ", ""),
                            "role": column_values[2].split(" ")[0].replace(" ", ""),
                            "mac": column_values[3].replace(" ", "")
                         }
                }
    return racks 


def check_asset(sn):
    if len(get_client("assets", method="GET", data={"asset_sn": sn})) > 0:
        return True
    else:
        return False

def create_asset(regions, channels, models, sn, classify):
    asset_data = {
            "asset_model": models[0]['id'],
            "asset_sn": sn,
            "asset_channel": channels[0]['id'],
            "asset_order_num": "xxx",
            "asset_invoice_num": "xxx",
            "asset_occasion": "2013-08-12",
            "asset_over_protection_date": "2013-08-12",
            "asset_classify": classify,
            "asset_extend_value": "",
            "asset_area": 3,
            "asset_region": regions[0]['id'],
            "asset_department": 1
    }
    get_client("assets", method="POST", data=asset_data)
    #print(asset_data)

def write_node(last_raw, node_info, sheet):
    sheet.write(last_raw+1, 1, node_info['info']['sn'])
    sheet.write(last_raw+1, 0, node_info['info']['id'])
    sheet.write(last_raw+1, 2, node_info['info']['ip'])
    disk_raw = last_raw
#    for disk in node_info['disks']:
#        if node_info['disks'][disk] != None:
#            disk_raw += 1
#            sheet.write(disk_raw, 4, node_info['disks'][disk]["sn"])
#            sheet.write(disk_raw, 3, node_info['disks'][disk]["id"])
    if disk_raw > last_raw:
        return disk_raw
    else:
        return last_raw + 1


def write_excel(path, racks_info):
    last_raw = 0

    wbk = xlwt.Workbook(encoding="utf-8", style_compression=0)
    sheet = wbk.add_sheet(u"服务器硬盘标签信息", cell_overwrite_ok=True)
    sheet.write(last_raw, 0, u"UOS ID")
    sheet.write(last_raw, 1, u"服务器SN")
    sheet.write(last_raw, 2, u"IP")
    sheet.write(last_raw, 3, u"DISK UOS ID")
    sheet.write(last_raw, 4, u"DISK SN/WWN")
    for rack in racks_info:
        for node in racks_info[rack]:
            last_raw = write_node(last_raw, racks_info[rack][node], sheet)
    wbk.save(path)


if __name__ == '__main__':
    options = generate_options() 
    worksheet = get_worksheet(options.file)
    racks_info = get_node_info_from_worksheet(worksheet)
    if options.method == "check_sheet":
        for rack_info in racks_info:
            pass
    elif options.method == "asset_generate":
        print options.region
        regions = get_client("regions", method="GET", data={"region_name": options.region})
        channels = get_client("channels", method="GET", data={"channel_name": "Borrow"})
        for rack in racks_info:
            if check_asset(rack):
                pass
            else:
                print rack
            for node in racks_info[rack]:
                node_info = racks_info[rack][node]
                node_sn = node_info['info']['sn']
                if not check_asset(node_sn):
                    model_name = node_info['info']['model']
                    print model_name
                    models = get_client("models", method="GET", data={"model_name": model_name})
                    create_asset(regions, channels, models, node_sn, "node")
#                for disk in node_info['disks']:
#                    disk_data = node_info['disks'][disk]
#                    print disk_data
#                    if disk_data != None and not check_asset(disk_data):
#                        models = get_client("models", method="GET", data={"model_name": "SSDSC2BB480G4"}) 
#                        create_asset(regions, channels, models, disk_data, "module")
    elif options.method == "info_generate":
        starts = {
                "Compute": 68,
                "Network": 64,
                "Hyper": 233,
                "Storage": 201
        }

        regions = get_client("regions", method="GET", data={"region_name": options.region})
        assets = get_client("assets", method="GET", data={"asset_region": regions[0]['id']})
        searchable_assets = {}
        for asset in assets:
            searchable_assets[asset['asset_sn']] = asset
        for rack in racks_info:
            for node in racks_info[rack]:
                racks_info[rack][node]['info']['id'] = searchable_assets[racks_info[rack][node]['info']['sn']]['id']
                racks_info[rack][node]['info']['ip'] = options.prefix + str(starts[racks_info[rack][node]['info']['role']])
                starts[racks_info[rack][node]['info']['role']] += 1
#                for disk in racks_info[rack][node]['disks']:
#                    if racks_info[rack][node]['disks'][disk] != None:
#                        print racks_info[rack][node]['disks'][disk]
#                        racks_info[rack][node]['disks'][disk] = {
#                                "sn": racks_info[rack][node]['disks'][disk],
#                                "id": searchable_assets[racks_info[rack][node]['disks'][disk]]['id']
#                        }
        write_excel(options.tagexcel, racks_info)
        write_files(racks_info)
