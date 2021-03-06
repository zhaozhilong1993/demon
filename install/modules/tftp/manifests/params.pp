# TFTP defaults
class tftp::params {
  case $::osfamily {
    'Debian': {
      $package = 'tftpd-hpa'
      $daemon  = true
      $service = 'tftpd-hpa'
      if $::operatingsystem == 'Ubuntu' {
        $root = '/var/lib/tftpboot'
      } else {
        $root = '/srv/tftp'
      }
      if  ($::operatingsystem == 'Ubuntu' and versioncmp($::operatingsystemrelease, '14.10') >= 0) or
          ($::operatingsystem == 'Debian' and versioncmp($::operatingsystemrelease, '8') >= 0) {
        $syslinux_package = [ 'syslinux-common', 'pxelinux' ]
      } else {
        $syslinux_package = 'syslinux'
      }
    }
    'RedHat': {
      $package          = 'tftp-server'
      $daemon           = false
      $syslinux_package = 'syslinux'
      if $::operatingsystemrelease =~ /^(4|5)/ {
        $root  = '/tftpboot'
      } else {
        $root  = '/var/lib/tftpboot'
      }
    }
    'Linux': {
      case $::operatingsystem {
        'Amazon': {
          $package          = 'tftp-server'
          $daemon           = false
          $root             = '/var/lib/tftpboot'
          $syslinux_package = 'syslinux'
        }
        default: {
          fail("${::hostname}: This module does not support operatingsystem ${::operatingsystem}")
        }
      }
    }
    /^(FreeBSD|DragonFly)$/: {
      $package = 'tftp-hpa'
      $daemon  = true
      $service = 'tftpd'
      $root = '/tftpboot'
      $syslinux_package = 'syslinux'
    }

    default: {
      fail("${::hostname}: This module does not support osfamily ${::osfamily}")
    }
  }
}
