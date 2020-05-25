#!/usr/bin/env python3

from scapy.all import *
from scapy.layers.http import HTTPRequest
from .banner import RED, RESET, BLUE, GREEN

class sniff:

    def  __init__(self, sraw=False, iface=None):
        self.iface = iface
        self.sraw = sraw
    
    def process_packet(self, packet):
        if packet.hashlayer(HTTPRequest):
            URL = packet[HTTPRequest].Host.decode() + packet[HTTPRequest].Path.decode()
            IP = packet[IP].src
            METHOD = packet[HTTPRequest].Method.decode()
            print(f"{IJO}[{METHOD}] {IP} Requested {URL}")
            if self.sraw and packet.haslayer(Raw) and method == "POST":
                 print(f"\n{RED}[*] Some useful Raw data: {packet[Raw].load}")
