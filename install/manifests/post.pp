$scriptdir=hiera('scriptdir')

file { '/etc/puppet/hieradata':
  ensure => directory,
}
file { '/etc/puppet/autosign.conf':
  ensure  => present,
  content => "*\n",
}
file { '/opt/puppet/':
  ensure => directory,
}
file { '/etc/puppet/hiera.yaml':
  ensure => present,
  source => "$scriptdir/files/hiera.yaml",
}
package { 'yaml-lint':
  ensure   => present,
  source   => "$scriptdir/files/yaml-lint-0.0.7.gem",
  provider => 'gem',
}
