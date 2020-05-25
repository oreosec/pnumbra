#!/usr/bin/env python3

import re
import configparser
import os
import ipaddress

class config:
    def __init__(self, limit, interface="wlan0"):
        self.limit = limit
        self.interface = interface
        self.ssid = ""
        self.ch = ""
        self.karma = False
        self.ap_dict = dict()
        self.dhcp_dict = dict()

    def APconf(self):
        self.ap_dict = {
            'interface' : self.interface,
            'driver' : 'nl80211',
            'ssid' : self.ssid,
            'channel' : self.ch,
            'hw_mode' : 'g',
            'macaddr_acl' : 0,
            'ignore_broadcast_ssid' : 0,
            'auth_algs' : 1,
            'wme_enabled' : 1
        }
        if self.karma:
            self.ap_dict["karma_enable"] = 1
        return self.ap_dict

    def DHCPconf(self):
        _, first_ip, few = self.get_dhcp_ip()
        self.dhcp_dict = {
            'interface' : ''.join(self.interface),
            'dhcp-range' : '{},{},12h'.format(first_ip, few),
            'listen-address' : '127.0.0.1'
        }
        return self.dhcp_dict

    @staticmethod
    def check_ip(ip):
        try:
            ip = ipaddress.IPv4Address(ip)
        except ipaddress.AddressValueError:
            print("Maybe your DHCP IP was invalid.. check in config.ini")
    
    def get_dhcp_ip(self):
        configs = configparser.ConfigParser()
        configs.read("config.ini")
        ip = configs['dhcp']['ip']
        self.check_ip(ip)
        gateway = ipaddress.IPv4Address(ip)
        first_ip = gateway + 1
        few = gateway + 99
        return gateway, first_ip, few


    def process(self):
        PATH = "core/config"
        HOSTAPD = os.path.join(PATH, "hostapd.conf")
        DNSMASQ = os.path.join(PATH, "dnsmasq.conf")
        reditems = []

        with open(HOSTAPD, "w") as f:
            APconfig = self.APconf()
            for key, value in APconfig.items():
                print("{}={}".format(key, value), file=f)

        with open(DNSMASQ, "w") as x:
            DHCPconfig = self.DHCPconf()
            print("no-resolv", file=x)

            for key, value in DHCPconfig.items():
                print("{}={}".format(key, value), file=x)
            
            gateway, _, j = self.get_dhcp_ip()
            option = ['3,{}'.format(gateway),'6,{}'.format(gateway)]
            for options in option:
                print('dhcp-option=' + options, file=x)
            configs = configparser.ConfigParser()
            configs.read("config.ini")
            if configs['more']['captive_portal'] == 'on':
                for key in configs['captive_portal']:
                    print("address=/"+key+"/"+configs['captive_portal'][key], file=x)
            if self.limit:
                for key in configs['Redirect']:
                    print("address=/"+key+"/"+configs['Redirect'][key], file=x)
            else:
                print("address=/#/{}".format(gateway), file=x)
                
  

if __name__ == "__main__":
    a = config(False)
    a.process()