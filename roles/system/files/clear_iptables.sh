#!/bin/bash

iptables -F
iptables -X
iptables -F -t nat
iptables -X -t nat
iptables -F -t mangle
iptables -X -t mangle
iptables-save > /etc/sysconfig/iptables
