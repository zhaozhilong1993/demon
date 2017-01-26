#! /usr/bin/env python

import optparse
import sys

#def generate_options():
#    p = optparse.OptionParser()
#    p.add_option("--ip", "-i")
#    options, argument = p.parse_args()
#    return options

def main():
    ip_list = []
    ipstr = ''
    #options = generate_options()
    ip = sys.argv[1:]
    for ele in ip:
	ipstr += ele
    if ipstr == '[]':
        raise ValueError,'No host found'
    #ip_list = (options.ip).strip('['']').split(',')
    ip_list = ipstr.strip('['']').split(',')
    ip_begin = ip_list[0].split('.')[-1]
    ip_end = ip_list[-1].split('.')[-1]
    newList = "[%s-%s]" %(ip_begin, ip_end)
    sys.stdout.write(newList)

if __name__ == '__main__':
    main()
