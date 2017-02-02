#!/bin/bash -e -u
CWD=$(dirname $0)
DIR=$(realpath $CWD)

# Set script path in config.yaml
sed -ri "s|(scriptdir:).*|\1 $DIR|" $DIR/config.yaml
sed -ri "s|(.*:datadir:).*|\1 $DIR|" $DIR/hiera.yaml

# Get hostname in config.yaml
HOSTNAME=$(sed -nr "s/hostname:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
DOMAIN=$(sed -nr "s/^domain:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
MANAGER_NETWORK_PREFIX=$(sed -nr "s/manager_network:[[:space:]]*(.*)/\1/p" $DIR/config.yaml| awk -F. '{print $1"."$2"."$3}')
MANAGER_NETWORK_PREFIX_ID=$(sed -nr "s/manager_network:[[:space:]]*(.*)/\1/p" $DIR/config.yaml| awk -F. '{print $3}')
SERVERNAME=$(sed -nr "s/puppet_server_name:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
FOREMANSERVER=$(sed -nr "s#foreman_base_url:[[:space:]]*'http://(.*)'#\1#p" $DIR/config.yaml)
FQDN="${HOSTNAME}.${DOMAIN}"

# Create hiera
#INVENTORY_FILE="${MANAGER_NETWORK_PREFIX_ID}.${DOMAIN}.ustack.in"
echo $DOMAIN
#ansible-playbook -vvv -i /root/ctask/inventory/${DOMAIN} /root/ctask/define/create_cluster/001.create_cluster_info.do.yaml  -k
#ansible-playbook -vvv -i /root/ctask/inventory/${DOMAIN} /root/ctask/define/create_cluster/002_1.config_foreman_proxy.yaml  -k
ansible-playbook -vvv -i /root/ctask/inventory/${DOMAIN} /root/ctask/define/create_cluster/003.provision_pre.do.yaml  -k
