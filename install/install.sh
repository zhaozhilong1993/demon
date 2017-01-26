#!/bin/bash -e -u
CWD=$(dirname $0)
DIR=$(realpath $CWD)

# Set script path in config.yaml
sed -ri "s|(scriptdir:).*|\1 $DIR|" $DIR/config.yaml
sed -ri "s|(.*:datadir:).*|\1 $DIR|" $DIR/hiera.yaml

# Get hostname in config.yaml
HOSTNAME=$(sed -nr "s/hostname:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
DOMAIN=$(sed -nr "s/domain:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
SERVERNAME=$(sed -nr "s/puppet_server_name:[[:space:]]*(.*)/\1/p" $DIR/config.yaml)
FOREMANSERVER=$(sed -nr "s#foreman_base_url:[[:space:]]*'http://(.*)'#\1#p" $DIR/config.yaml)
FQDN="${HOSTNAME}.${DOMAIN}"

# Set hostname
hostname $HOSTNAME
cp ${DIR}/files/network /etc/sysconfig/network
sed -ri "s/(HOSTNAME=).*/\1$HOSTNAME/" /etc/sysconfig/network
sed -i "s/foreman.ustack.com/$SERVERNAME/" $DIR/../scripts/initial/foreman_setting.py
if [ `grep  $SERVERNAME /etc/hosts | wc -l` -ne 0 ];then
  sed -i "s/.*$SERVERNAME/$FOREMANSERVER $SERVERNAME/g" /etc/hosts
else
  sed -i "/foreman.ustack.com/d" /etc/hosts
  echo "$FOREMANSERVER $SERVERNAME" >> /etc/hosts
fi



# Get puppetdb version
if ! yum list puppetdb &> /dev/null; then
  echo -e "\033[0;31mERROR: Not found PuppetDB in YUM repo, Check your yum repo settings.\033[0m"
  exit 3
fi
puppetdb_version=$(yum list puppetdb | grep -m 1 puppetdb | awk '{print $2}')
sed -ri "s|(puppetdb::globals::version:).*|\1 $puppetdb_version|" $DIR/config.yaml

# Install puppet
yum install -y puppet tmux

# Set FQDN
puppet resource host puppet ip=127.0.0.1 name=${FQDN} host_aliases=${HOSTNAME}

# Generate SSL cert
puppet cert generate $FQDN &> /dev/null

# Config puppet-master
puppet apply --parser=future --hiera_config=${DIR}/hiera.yaml --modulepath=${DIR}/modules --templatedir=${DIR}/templates -t ${DIR}/manifests/puppet.pp

# Post config
puppet apply --parser=future --hiera_config=${DIR}/hiera.yaml --modulepath=${DIR}/modules -t ${DIR}/manifests/post.pp

# Generate environment config
rm -rf /etc/puppet/environments/{common,example_env}
for dir in /etc/puppet/environments/*; do
  env=$(basename $dir)
  if [ -d $dir ]; then
    cp $DIR/templates/environment.conf $dir/environment.conf
    sed -ri "s|ENV|$env|" $dir/environment.conf
    if [ ! -e $dir/manifests/cluster ]; then
      mkdir $dir/manifests/cluster
    fi
  fi
done

# Insert foreman.psql
systemctl stop httpd.service
su - postgres << EOF
psql -c "DROP DATABASE foreman;"
psql -c "CREATE DATABASE foreman;"
psql -c "GRANT ALL PRIVILEGES ON DATABASE foreman to foreman;"
EOF
PGPASSWORD=ustack psql -h localhost -U foreman -d foreman -f foreman.psql

# Reset foreman admin password
foreman-rake permissions:reset

# Restart puppet
systemctl restart httpd.service
