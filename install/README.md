# Puppet Bootstrap
此项目用来快速的搭建起一个 Puppet master + PuppetDB + foreman 的环境

## Environment support
目前只支持 CentOS7

## Prerequisite
- 配置好的仓库，需要包含 foreman/puppet/puppetdb/postgresql 等软件包
- 主机名，puppet 依赖于 FQDN，因此需要配置好主机名（此项目可以自动配置）
- CentOS7 x86-64 系统

## Installation
- 将项目最新版克隆到需要安装 puppet master 的机器上，如 `/root/puppet-bootstrap`

- 填写 `config.yaml`，此文件中需要填写的条目有:

`installrepo`: 是否使用外网源

`hostname`: 主机名

`domain`: 域名

`servername`: foreman 的访问域名

`db_password`: foreman 数据库的密码

`admin_password`: foreman admin 账户的密码

`logging_level`: foreman 的日志级别

`dhcp_proxy`: 是否开启 dhcp 的 proxy

`dhcp_interface`: DHCP 服务接口名称

`dhcp_gateway`:  网关地址

`foreman_base_url`: foreman 的地址


- 执行 `install.sh`，开始安装

- 等待一杯咖啡的时间，puppet/puppetDB/foreman/foreman-proxy 就安装好了

## Postinstallation
安装完成后, 默认会创建 `production`  和 `liberty` 两个 `environment`，如果需要增加其他的 environment，可以在 `config.yaml` 中增加新的 environment

### Setup puppet code
每个环境需要对应的 manifest 和 modules，将 puppet 代码（包含 sunfire/storm/karma）放到 `/opt/puppet/ENVIRONMENT` 目录下，其中的 `ENVIRONMENT` 表示环境名（如 liberty）。

然后将 sunfire/storm/karma 中所有的目录链接到对应环境的 modules 目录下，例如 liberty 环境：

```
ln -s /opt/puppet/liberty/sunfire/* /etc/puppet/environments/liberty/modules/
ln -s /opt/puppet/liberty/storm/* /etc/puppet/environments/liberty/modules/
ln -s /opt/puppet/liberty/karma/* /etc/puppet/environments/liberty/modules/
```

### 导入 foreman 数据
先停掉 httpd 服务：
`systemctl stop httpd`

然后切换到 postgres 用户 drop 掉 foreman 数据库，并重建：
```
$ su - postgres
$ psql
postgres=# DROP DATABASE foreman;
postgres=# CREATE DATABASE foreman;
postgres=# GRANT ALL PRIVILEGES ON DATABASE foreman to foreman;
postgres=# \q
$ exit
```

重新导入数据，并启动服务
```
$ PGPASSWORD=ustack psql -h localhost -U foreman -d foreman -f foreman.psql
$ systemctl start httpd
```

登录 foreman WEB 界面，密码为默认密码

### 常见问题
1. 目前需要手动在 foreman UI 上添加 smart proxy，在添加时需要写上 smart proxy  API  接口的地址，由于部署的 Foreman proxy 使用 HTTPS  接口，因此需要使用 HTTPS 的格式，并且使用域名的方式（因为 HTTPS 验证必须使用和证书中匹配的域名），例如： `https://puppet.example.com:8443`。

2. 安装完成后，最好在本机运行 puppet agent -t 测试下 puppet master 是否正常，如果此时报错（很长很长的报错...），那么执行下面的操作：

停止 httpd

`systemctl stop httpd`

把 puppet 启在前台

`puppet master --no-daemonize`

Ctrl + C 取消，然后启动 httpd

`systemctl start httpd`
