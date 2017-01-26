#!/usr/bin/env python
# encoding: utf-8

import paramiko, base64
import optparse
import json

def generate_options():
    p = optparse.OptionParser()
    p.add_option("--address", "-a")
    p.add_option("--username", "-u")
    p.add_option("--password", "-p")
    options, argument = p.parse_args()
    return options

if __name__ == '__main__':
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    options = generate_options() 

    address = options.address
    username = options.username
    password = options.password
    
    try:
        client.connect(address, username=username, password=password, timeout=1)
        stdin, stdout, stderr = client.exec_command('ls')
    except Exception, e:
        print "Fail"
    else:
        print "Success"
    finally:
        client.close()
