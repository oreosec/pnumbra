#!/usr/bin/env python3

from threading import Thread
from .config.config import config
from .begin import execute_commands
from subprocess import PIPE, Popen
import os
import netifaces
from .banner import warn, info, ok
import configparser


class accesspoint:
    def __init__(self, interface, karma):
        self.interface = interface
        self.karma = karma

    @staticmethod
    def iface_upper(interface):
        addr = netifaces.ifaddresses(interface)
        if not netifaces.AF_INET in addr:
            conf = configparser.ConfigParser()
            conf.read("config.ini")
            ip = conf["dhcp"]["ip"]
            execute_commands(['ifconfig ' +interface+ ' {}/24 up'.format(ip)])

    @staticmethod
    def check_interface(interface):
        try:
            addr = netifaces.ifaddresses(interface)
        except ValueError:
            warn("Interface was'nt valid!!")
            exit()

    def make_config(self, limit, ssid, ch):
        conf = config(limit, self.interface)
        conf.ssid = ssid
        conf.ch = ch
        if self.karma:
            conf.karma = True
        conf.process()
        
        PATH_DIR = os.path.abspath(os.curdir)
        self.hostapd_path = os.path.join(PATH_DIR, "hostapd-2_6/hostapd/hostapd")
        self.hostapd_conf = os.path.join(PATH_DIR, "core/config/hostapd.conf")
        self.dnsmasq_conf = os.path.join(PATH_DIR, "core/config/dnsmasq.conf")


# memulai AP
    def startAP(self):
        a = Popen([self.hostapd_path, self.hostapd_conf], stdout=PIPE, stderr=PIPE)
        # a.communicate()
        with open("logs/accesspoint.log", "w") as f:
            for i in a.communicate():
                print(i.decode(), file=f)
    def startDHCP(self):
        a = Popen(['dnsmasq', '-C', self.dnsmasq_conf, '-d'], stdout=PIPE, stderr=PIPE)
        # a.communicate()
        with open("logs/dhcp.log", "w") as x:
            for i in a.communicate():
                print(i.decode(), file=x)

# menyalakan accesspoint
#     info("Startting Access Point")
#     ap = Thread(target=startAP, args=[CONFIG_FILE])
#     ap.daemon = True
#     ap.start()
#     ok("Access Point started")
# menyalakan dhcp
#     dhcp = Thread(target=startDHCP, args=[DNSMASQCONF])
#     dhcp.daemon = True
#     dhcp.start()


# firewall
    # clear_rules()
    # nat(IINTERNET, IFACE)
    # redirect_localhost()

