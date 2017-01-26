#/bin/bash
#
# 这是一个临时脚本 #
# 确保所有的db sync均被执行
#
PATH="/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin:/opt/dell/srvadmin/bin:/opt/dell/srvadmin/sbin:/root/bin"
source /root/openrc
## cinder ##
cinder-manage db sync
## designate ##
designate-manage database-init
## glance ##
glance-manage db_sync
## gondor ##
gondor-db-manage --config-file /etc/gondor/gondor.conf upgrade head
## keystone mysql init ##
keystone-manage db_sync
keystone-manage db_sync --extension uos_account
## gringotts ##
gring-dbsync
/etc/init.d/openstack-nova-api restart
/etc/init.d/openstack-cinder-api restart
/etc/init.d/openstack-glance-api restart
/etc/init.d/neutron-server restart
/etc/init.d/httpd restart
## kiki ##
/usr/bin/kiki-dbsync
## lotus ##
/usr/bin/lotus-dbsync
## manila ##
manila-manage db sync
## neutron ##
neutron-db-manage --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head
## nova ##
/usr/bin/nova-manage db sync
## placebo ##
python /usr/share/placebo/manage.py syncdb --noinput --migrate
## tars ##
python /usr/share/tars/manage.py syncdb --noinput --migrate
## ticket ##
/usr/bin/ticket-dbsync
## ustack_www ##
python /usr/share/ustack_www/manage.py syncdb --noinput --migrate
## vmmanager ##
/usr/bin/vm_manager-dbsync
