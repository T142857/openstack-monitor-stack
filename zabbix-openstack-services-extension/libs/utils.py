import os
import sys
import json
import logging
import requests
import ConfigParser
from datetime import datetime
from dateutil.tz import tzlocal

import keystoneclient.v3.client as ksclient
from novaclient.client import Client as novaclient
from cinderclient import client as cinclient
import neutronclient.v2_0.client as neuclient


def print_json(data):
    """formar data to json"""
    print json.dumps({'data': data}, sort_keys=True, indent=7, separators=(',', ':'))


def read_env(path):
    """read file line by line in to list"""
    env = []
    with open(path) as file_path:
        for line in file_path:
            line = line.strip()
            env.append(line)
    return env


def remove_duplicate(list_array):
    """remove element duplicate on list"""
    return list(set(list_array))


def prepare_session(func):
    def wrapper(self, **kwargs):
        config_parser = ConfigParser.RawConfigParser()
        config_parser.read(os.path.dirname(os.path.realpath(__file__)) + "/.env")
        url = config_parser.get('default', 'url')
        user_id = config_parser.get('default', 'user_id')
        password = config_parser.get('default', 'password')
        project_id = config_parser.get('default', 'project_id')

        auth = OpenstackIdentityManager(url, user_id, password, project_id, nova_version=2, cinder_version=2)
        auth.get_token
        user_info = auth.identity_info
        if user_info["auth_token"]:
            self.openstack_services = OpenstackServiceManager(username=user_info["username"], nova_version=2,
                                                              cinder_version=2,
                                                              auth_token=user_info["auth_token"],
                                                              project_id=user_info["project_id"],
                                                              neutron_endpoint=user_info["neutron_endpoint"],
                                                              nova_endpoint=user_info["nova_endpoint"],
                                                              cinder_endpoint=user_info["cinder_endpoint"])
            if 'is_neutron' in kwargs and kwargs["is_neutron"]:
                self.neutron_pattern = config_parser.get('default', 'neutron_pattern')
            func(self, **kwargs)
        else:
            sys.exit()

    return wrapper


class OpenstackIdentityManager(object):
    def __init__(self, url, user_id, password, project_id, nova_version=2, cinder_version=2):
        self.url = url
        self.user_id = user_id
        self.password = password
        self.project_id = project_id
        self.nova_version = nova_version
        self.cinder_version = cinder_version
        self.identity_info = None
        self.token_expired = None

    def get_credentials(self):
        """
        :return dict {username, password, auth_url, project_id}.
        """
        d = {'user_id': self.user_id, 'password': self.password, 'auth_url': self.url + '/v3',
             'project_id': self.project_id}
        return d

    @property
    def get_token(self):
        """
        :return dict {'url': _, 'password': _, 'auth_url'}
        """
        try:
            credentials = self.get_credentials()
            keystone = ksclient.Client(**credentials)
            d = {'url': self.url, 'password': self.password, 'auth_url': credentials['auth_url'],
                 'nova_version': self.nova_version, 'cinder_version': self.cinder_version,
                 'domain_id': keystone.auth_ref.user_domain_id, 'username': keystone.auth_ref.username,
                 'project_id': keystone.project_id, 'project_name': keystone.project_name,
                 'project_domain_id': keystone.auth_ref.project_domain_id, 'user_id': keystone.user_id,
                 'auth_token': keystone.auth_token,
                 'glance_endpoint': keystone.service_catalog.url_for(service_type='image'),
                 'neutron_endpoint': keystone.service_catalog.url_for(service_type='network'),
                 'nova_endpoint': keystone.service_catalog.url_for(service_type='compute'),
                 'cinder_endpoint': keystone.service_catalog.url_for(service_type='volumev2'),
                 'ceilometer_endpoint': keystone.service_catalog.url_for(service_type='metering')}
            self.identity_info = d
            return d
        except Exception as e:
            raise e


class OpenstackServiceManager(object):
    """docstring for DiscoveryServiceManager"""

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.nova_version = kwargs['nova_version']
        self.project_id = kwargs['project_id']
        self.cinder_version = kwargs['cinder_version']
        self.auth_token = kwargs['auth_token']
        self.neutron_endpoint = kwargs['neutron_endpoint']
        self.nova_endpoint = kwargs['nova_endpoint']
        self.cinder_endpoint = kwargs['cinder_endpoint']

    def get_nova_services(self):
        """nova services discovery
            return:
        """
        try:
            # authentication
            nova = novaclient(self.nova_version, self.username,
                              self.auth_token,
                              project_id=self.project_id,
                              auth_url=self.nova_endpoint,
                              insecure=False,
                              cacert=None)
            nova.client.auth_token = self.auth_token
            nova.client.management_url = self.nova_endpoint
            return nova.services.list()
        except Exception as e:
            raise e

    def get_neutron_agents(self):
        """ neutron agents discovery"""
        try:
            headers = {"User-Agent": "python-neutronclient", "Accept": "application/json",
                       "X-Auth-Token": self.auth_token}
            # print headers
            r = requests.get(self.neutron_endpoint+'/v2.0/agents.json', headers=headers)
            return json.loads(r.content)
        except Exception as e:
            raise e

    def get_cinder_services(self):
        try:
            cinder = cinclient.Client(self.cinder_version, self.username,None, auth_url=self.cinder_endpoint)
            cinder.client.auth_token = self.auth_token
            cinder.client.management_url = self.cinder_endpoint
            return cinder.services.list()
        except Exception as e:
            raise e

    # def get_cinder_services(self, username, password, auth_url):
    #     try:
    #         cinder = cinclient.Client(self.cinder_version, username, password, None, auth_url)
    #         cinder.client.auth_token = self.auth_token
    #         cinder.client.management_url = self.cinder_endpoint
    #         return cinder.services.list()
    #     except Exception as e:
    #         raise e
