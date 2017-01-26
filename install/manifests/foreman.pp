$servername = hiera('servername')
$db_password = hiera('db_password')
$admin_password = hiera('admin_password')
$logging_level = hiera('logging_level')
class { 'foreman':
  servername             => $servername,
  db_password            => $db_password,
  admin_password         => $admin_password,
  logging_level          => $logging_level,
  passenger_ruby         => '/usr/bin/ruby193-ruby',
  passenger_ruby_package => 'ruby193-rubygem-passenger-native',
  plugin_prefix          => 'ruby193-rubygem-foreman_',
  custom_repo            => true,
  configure_epel_repo    => false,
  configure_scl_repo     => false,
}

# For puppet compatibility
apache::listen { '8140': }
