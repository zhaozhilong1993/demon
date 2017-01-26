$enable_foreman = hiera('enable_foreman')
$enable_foreman_proxy = hiera('enable_foreman_proxy')
$enable_yumrepo = hiera('enable_yumrepo')
$enable_ntpserver = hiera('enable_ntpserver')
$enable_install_deploy_tools = hiera('enable_install_deploy_tools')
$command_threads = inline_template("<%= [${::processorcount}/2, ${::processorcount}-2].max %>")
$max_threads = inline_template("<%= [(${::processorcount}*1.5).floor, 15].max %>")
$server_environments = hiera('server_environments')
$puppet_server_name = hiera('puppet_server_name')
$db_password = hiera('db_password')
$admin_password = hiera('admin_password')
$logging_level = hiera('logging_level')
$dhcp = hiera('dhcp_proxy')
$dhcp_interface = hiera('dhcp_interface')
$dhcp_gateway = hiera('dhcp_gateway')
$foreman_base_url = hiera('foreman_base_url')

Exec {
  path => ['/bin', '/sbin', '/usr/bin', '/usr/sbin']
}

class { '::puppetdb':
  listen_address      => '0.0.0.0',
  manage_package_repo => false,
  command_threads     => $command_threads,
  max_threads         => $max_threads,
} ->

exec { 'setup puppetdb SSL cert':
  command => 'puppetdb ssl-setup -f &> /dev/null || return 0',
  unless  => 'test -f /etc/puppetdb/ssl/ca.pem',
  require => Service['puppetdb'],
} ~>

exec { 'restart puppetdb':
  command     => 'systemctl restart puppetdb',
  refreshonly => true,
  before      => [Puppetdb_conn_validator['puppetdb_conn'], Class['puppet']],
}

class { '::puppet':
  server                      => true,
  server_foreman              => false,
  server_external_nodes       => '',
  server_environments         => $server_environments,
  server_puppetdb_host        => $::fqdn,
  server_reports              => 'puppetdb,foreman',
  server_parser               => 'future',
  server_storeconfigs_backend => 'puppetdb',
}

if $enable_foreman {
  class { 'foreman':
    servername             => $puppet_server_name,
    db_password            => $db_password,
    admin_password         => $admin_password,
    logging_level          => $logging_level,
    passenger_ruby         => '/usr/bin/ruby193-ruby',
    passenger_ruby_package => 'ruby193-rubygem-passenger-native',
    plugin_prefix          => 'ruby193-rubygem-foreman_',
    custom_repo            => true,
    configure_epel_repo    => false,
    configure_scl_repo     => false,
    ssl                    => false,
  } ->
  file { '/usr/share/foreman/.ssh/config':
    ensure  => file,
    mode    => '0644',
    content => "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null",
  }
}

if $enable_foreman_proxy {
  class { 'foreman_proxy':
    custom_repo             => true,
    dhcp                    => true,
    dhcp_interface          => $dhcp_interface,
    dhcp_gateway            => $dhcp_gateway,
    bmc                     => true,
    http                    => true,
    http_port               => 8443,
    foreman_base_url        => $foreman_base_url,
    trusted_hosts           => [],
    ssl                     => false,
    dhcp_split_config_files => false,
    dhcp_listen_on          => 'http',
    tftp_listen_on          => 'http',
  }
  class { 'foreman::compute::libvirt':
  }

  file { '/data0':
    ensure => directory,
  }
  apache::vhost { 'installmedia':
    add_default_charset => 'UTF-8',
    docroot             => '/data0/images/',
    ip                  => $listen_interface,
    options             => ['Indexes FollowSymLinks'],
    port                => 8000,
    priority            => '06',
    servername          => 'media.ustack.com',
    require             => File['/data0'],
  }
  Class['foreman'] -> Class['foreman_proxy']
}
if $enable_yumrepo {
  apache::vhost { 'yumrepo':
    add_default_charset => 'UTF-8',
    docroot             => '/var/',
    ip                  => $listen_interface,
    options             => ['+Indexes'],
    port                => 80,
    priority            => '07',
    servername          =>  'mirrors.ustack.com',
  }
}
if $enable_install_deploy_tools {
  $package_list = [ "ansible", "python-requests", "nmap", "clustershell" ]
  package { $package_list:
    ensure =>  latest,
  }
  file { '/etc/clustershell/groups':
    ensure  => file,
    mode    => '0644',
    content => template('groups'),
    require => Package[$package_list],
  }
  file { '/etc/ansible/ansible.cfg':
    ensure  => file,
    mode    => '0644',
    content => template('ansible.cfg'),
    require => Package[$package_list],
  }
  file { '/usr/bin/e':
    ensure  => file,
    mode    => '0755',
    content => template('e'),
  }
}
if $enable_ntpserver {
  class { '::ntp':
    servers => [ '0.asia.pool.ntp.org', '1.asia.pool.ntp.org', '2.asia.pool.ntp.org', '3.asia.pool.ntp.org' ],
    udlc    => true,
  }
}
