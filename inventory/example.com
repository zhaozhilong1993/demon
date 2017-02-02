[Hypervisor]
10.0.215.[31:32]

[Controll]
10.0.215.[41:42]

[Network]
10.0.215.[65:65]

[Compute]
10.0.215.[68:68]

[Loaderbalance]
10.0.215.[34:35]

[MQ]
10.0.215.[44:46]

[Cache]
10.0.215.[47:47]

[Mysql]
10.0.215.[50:52]

[CephMonitor]
10.0.215.[61:63]

[localhost]
10.0.215.32

[vip_address]
10.0.215.37

[puppet_server_ip]
10.0.215.32

[example.com:children]
Hypervisor
Controll
Network
Compute
Loaderbalance
MQ
Cache
Mysql
CephMonitor
localhost
vip_address
puppet_server_ip
