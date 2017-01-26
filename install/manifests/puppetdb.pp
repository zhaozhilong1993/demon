$command_threads = inline_template("<%= [${::physicalprocessorcount}/2, ${::physicalprocessorcount}-2].max %>")
$max_threads = inline_template("<%= [(${::physicalprocessorcount}*1.5).floor, 15].max %>")

class { '::puppetdb':
  listen_address      => '0.0.0.0',
  manage_package_repo => false,
  command_threads     => $command_threads,
  max_threads         => $max_threads,
}
