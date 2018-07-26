"""
JokerBui @2017
Contact: bui.songtoan
"""
#!/usr/bin/python

from libs.utils import *

import argparse



class NovaServicesDiscovery(object):
    @prepare_session
    def __init__(self, **kwargs):
        self.services = self.openstack_services.get_nova_services()

    def discovery_hosts(self, argv):
        """Discovery hosts"""
        out = []
        # discovery controller services
        if argv == 'discovery_controller_hosts':
            c_services = []
            for service in self.services:
                if service.zone == 'internal':
                    c_services.append(service.host)
            # remove element duplicate in list
            for c in remove_duplicate(c_services):
                out.append({"{#OPENSTACK_NOVA_CONTROLLER}": c})
        # discovery nova compute services
        elif argv == 'discovery_compute_hosts':
            for service in self.services:
                if service.zone != 'internal':
                    out.append({"{#OPENSTACK_NOVA_COMPUTE}": str(service.host)})
        return out

    def service_state(self, host, service):
        """Check nova service state"""
        for s in self.services:
            if s.host == host and s.binary == service and s.state == 'up':
                return 1
        return 0


class NeutronServicesDiscovery(object):
    @prepare_session
    def __init__(self, **kwargs):
        self.agents = self.openstack_services.get_neutron_agents()

    def discovery_gw_hosts(self, argv):
        """Discovery neutron services on neutron gateway node"""
        out = []
        if argv == 'discovery_gw_hosts':
            c_services = []
            for agent in self.agents["agents"]:
                if self.neutron_pattern in agent["host"]:
                    c_services.append(agent["host"])
            for c in remove_duplicate(c_services):
                out.append({"{#OPENSTACK_NEUTRON_GW}": c})
        return out

    def discovery_compute_hosts(self, argv):
        """Discovery neutron service on compute node"""
        out = []
        if argv == 'discovery_compute_hosts':
            c_services = []
            for agent in self.agents["agents"]:
                if self.neutron_pattern not in agent["host"]:
                    c_services.append(agent["host"])
            for c in remove_duplicate(c_services):
                out.append({"{#OPENSTACK_NEUTRON_COMPUTE}": c})
        return out

    def service_state(self, host, agent):
        """Check neutron service up/down"""
        for a in self.agents["agents"]:
            if a["host"] == host and a["binary"] == agent and a["alive"] is True:
                return 1
        return 0


class CinderServicesDiscovery(object):
    @prepare_session
    def __init__(self, **kwargs):
        self.services = self.openstack_services.get_cinder_services()

    def discovery_controller_hosts(self, argv):
        """Discovery cinder controller hosts"""
        out = []
        if argv == 'discovery_controller_hosts':
            for service in self.services:
                if service.binary == 'cinder-scheduler':
                    out.append({"{#OPENSTACK_CINDER_CONTROLLER}": str(service.host)})
        return out

    def discovery_volume_hosts(self, argv):
        """Discovery cinder volume hosts"""
        out = []
        if argv == 'discovery_volume_hosts':
            for service in self.services:
                if service.binary == 'cinder-volume':
                    host = service.host
                    # zabbix not allowed character @ in item, replace @ to _
                    r_host = host.replace("@", "_")
                    out.append({"{#OPENSTACK_CINDER_VOLUME}": str(r_host)})
        return out

    def discovery_backup_hosts(self, argv):
        """Discovery cinder backup hosts"""
        out = []
        if argv == 'discovery_backup_hosts':
            for service in self.services:
                if service.binary == 'cinder-backup':
                    out.append({"{#OPENSTACK_CINDER_BACKUP}": str(service.host)})
        return out

    def service_state(self, host, service):
        """Check cinder serivce up/down"""
        host = host.replace("_", "@")
        for s in self.services:
            if s.host == host and s.binary == service and s.state == 'up':
                return 1
        return 0

def check_discovery_positive(value):
    """check discovery parameter in list"""
    discovery_list = ["discovery_controller_hosts", "discovery_compute_hosts", 
                             "discovery_volume_hosts", "discovery_backup_hosts", "discovery_gw_hosts"]
    str_value = str(value)
    if str_value not in discovery_list:
         raise argparse.ArgumentTypeError("%s is an invalid positive %s" % (value, discovery_list))
    return str_value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Openstack services monitoring')

    parser.add_argument('--project', required=True,
                        action="store",
                        help='openstack project. e.g: nova, neutron,...')
    parser.add_argument('--discovery', type=check_discovery_positive,
                        action="store",
                        help="discovery hosts. Include: discovery_controller_hosts, discovery_compute_hosts, "
                             "discovery_volume_hosts, discovery_backup_hosts")
    parser.add_argument('--service_state',
                        action='store_true',
                        help='service state')
    parser.add_argument('--host',
                        action='store',
                        help='host node')
    parser.add_argument('--service',
                        action='store',
                        help='service')

    args = parser.parse_args()
    # print args
    if args.project == 'nova':
        nova_services = NovaServicesDiscovery()
        if args.discovery in ['discovery_controller_hosts', 'discovery_compute_hosts']:
            print_json(nova_services.discovery_hosts(args.discovery))
        if args.service_state and args.host and args.service:
            print nova_services.service_state(args.host, args.service)

    if args.project == 'neutron':
        neutron_services = NeutronServicesDiscovery(is_neutron=True)
        if args.discovery == 'discovery_gw_hosts':
            print_json(neutron_services.discovery_gw_hosts(args.discovery))
        if args.discovery == 'discovery_compute_hosts':
            print_json(neutron_services.discovery_compute_hosts(args.discovery))
        if args.service_state and args.host and args.service:
            print neutron_services.service_state(args.host, args.service)
    
    if args.project == 'cinder':
        cinder_services = CinderServicesDiscovery()
        if args.discovery == 'discovery_controller_hosts':
            print_json(cinder_services.discovery_controller_hosts('discovery_controller_hosts'))
        if args.discovery == 'discovery_volume_hosts':
            print_json(cinder_services.discovery_volume_hosts('discovery_volume_hosts'))
        if args.discovery == 'discovery_backup_hosts':
            print_json(cinder_services.discovery_backup_hosts('discovery_backup_hosts'))
        if args.service_state and args.host and args.service:
            print cinder_services.service_state(args.host, args.service)
    
