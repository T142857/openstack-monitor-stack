Requirement
============
* keystoneclient
* novaclient
* cinderclient
* neutronclient
* requests

Openstack Model (KILO, MITAKA)
================
1. Controller nodes (eg: controller01, controller02, ...):
  * nova services: nova-scheduler, nova-conductor, nova-cert, nova-consoleauth
  * neutron services: neutron-server
  * cinder services: cinder-scheduler
2. Compute nodes:
  * nova services: nova-compute
  * neutron services: neutron-l3-agent, neutron-metata-agent, neutron-openvswitch-agent
3. Network Gateway nodes (eg: network-gw-01, network-gw-02,...):
  * neutron services: neutron-l3-agent, neutron-metata-agent, neutron-openvswitch-agent, neutron-dhcp-agent,...
4. Block Storage nodes:
  * cinder services: cinder-volume, cinder-backup
Install
========

```
# mkdir /etc/zabbix/scripts/
# cp -r libs/ openstack_services.py /etc/zabbix/scripts/
# chmod +x /etc/zabbix/scripts/openstack_services.py
```
Edit file /etc/zabbix/scripts/libs/.env
```
[default]
url = http://{IP}:35357
username = {USERNAME}
user_id = {USERID}
password = {PASSWORD}
project_id = {PROJECT_ID}
neutron_pattern = {NEUTRON_PATTERN}
```
Testing
========
Example discovery nova controller hosts
```
# /etc/zabbix/scripts/openstack_services.py --project nova --discovery discovery_controller_hosts
// return json data
{
       "data":[
              {
                     "{#OPENSTACK_NOVA_CONTROLLER}":"controller03"
              },
              {
                     "{#OPENSTACK_NOVA_CONTROLLER}":"controller02"
              },
              {
                     "{#OPENSTACK_NOVA_CONTROLLER}":"controller01"
              }
       ]
}

```
Example check services up/down
```
# /etc/zabbix/scripts/openstack_services.py --project nova --service_state --host controller01 --service nova-scheduler
// return 1 (up), 0 (down)
1
```
Import Template
================
import file userparameter_openstack_services.conf to zabbix server.
