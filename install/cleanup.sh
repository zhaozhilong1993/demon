#!/bin/bash -e -u
yum -y remove httpd puppet puppetdb foreman foreman-proxy
rm -rf /etc/puppetdb/ssl /var/lib/puppet/ssl /etc/puppet/ssl
