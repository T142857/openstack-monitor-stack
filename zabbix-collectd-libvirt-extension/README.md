force from: https://github.com/tcpcloud/Zabbix-Template-Linux-Collectd_libvirt

## Zabbix Template Linux Collectd_libvirt

### A Zabbix templates for libvirt stats

Tested on:
    CentOS 7.x X86_64, Collectd 4.10 Zabbix 3.0.x, KVM (kernel 3.10.x)
 
### installation - Manual (on zabbix-agent)
  - install collectd package(s) and perl modules
	```sh
	yum install epel-release
	yum install collectd collectd-virt perl-Collectd
	```
  - copy collectd.conf config file replace /etc/collectd.conf
  - copy userparameter_collectd_libvirt.conf config file into /etc/zabbix/zabbix_agentd.d/ folder
  - copy script "collect-libvirt-handler.pl" into /etc/zabbix/scripts/
    ```sh
	mkdir /etc/zabbix/scripts/
	cp collect-libvirt-handler.pl /etc/zabbix/scripts/
	chmod +x /etc/zabbix/scripts/collect-libvirt-handler.pl
	```
  - restart collectd & zabbix-agent service
    ```sh
	systemctl restart collectd.service
	systemctl restart zabbix-agent.service
	```
### import template (xml file)
### monitored items
  - virt-cpu-total - on all libvirt guests
  - disk operations READ - on all libvirt guests
  - disk operations WRITE - on all libvirt guests
  - disk octets READ - on all libvirt guests
  - disk octets WRITE - on all libvirt guests
  - network interface packets TR/RX - on all libvirt guests
  - network interface octets TR/RX - on all libvirt guests

  
