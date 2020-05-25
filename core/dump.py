#!/usr/bin/env python3

from scapy.all import *
from threading import Thread
from prettytable import PrettyTable
from colorama import init, Fore
from .banner import RED, RESET, BLUE, GREEN

class scanner:
	def __init__(self, timeout, interface="pnumbra-mon0"):
		self.interface = interface
		self.timeout = timeout
		self.dictionary = dict()

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
			self.dictionary[bssid] = [bssid, ssid, dbm_signal, channel, crypto]
			
	def change_channel(self):
	    ch = 1
	    while True:
	        os.system(f"iwconfig {self.interface} channel {ch}")
	        # switch channel from 1 to 14 each 0.5s
	        ch = ch % 14 + 1
	        time.sleep(0.5)

	def run(self):
		channel_changer = Thread(target=self.change_channel)
		channel_changer.daemon = True
		channel_changer.start()
		sniff(prn=self.callback, iface=self.interface, timeout=self.timeout)
		# print(self.networks)
		x = PrettyTable()
		x.field_names = ["BSSID", "SSID", "PWR", "CH", "ENC"]
		for key, value in self.dictionary.items():
			x.add_row(value)
		print(GREEN, x)
		


if __name__ == "__main__":
	a = scanner("wlan0mon")
	a.run()	

