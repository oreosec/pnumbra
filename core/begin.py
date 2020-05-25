#!/usr/bin/env python3

from colorama import init, Fore
from subprocess import PIPE, DEVNULL, Popen, check_output, STDOUT
import getpass
from .banner import *
import os

def execute_commands(commands):
    for command in commands:
        _, error = Popen(command.split(), stderr=PIPE, stdout=DEVNULL).communicate()
        if error:
            warn("has failed with the following error:")
            print(error.decode())

def check_root():
    if getpass.getuser() != "root":
        warn("Your previlege user has no root !!")
        info(" Shutting Down ..")
        exit()

# mengaktifkan fitur ip forward
def ip_route():
    file = "/proc/sys/net/ipv4/ip_forward"
    with open(file) as f:
        if f.read() == 1:
            return
    with open(file, "w") as f:
        print(1, file=f)

def monitor_mode(iface):
    Popen(['iw', 'dev', 'pnumbra-mon0', 'del'], stderr=DEVNULL).communicate()
    Popen(['ifconfig', iface, 'up'], stdout=DEVNULL, stderr=PIPE).communicate()
    with Popen(['iw', 'dev', iface, 'interface', 'add', 'pnumbra-mon0', 'type', 'monitor'], stdout=DEVNULL, stderr=PIPE) as makemon:
        error = makemon.communicate()[1].decode()
        if error != '':
            print("{RED}[!] Maybe your interface input was false or doesnt support monitor mode")
        else:
            up = Popen(['ifconfig', 'pnumbra-mon0', 'up'], stdout=DEVNULL)

def kill_monitor():
    p = Popen(['iw', 'dev', 'pnumbra-mon0', 'del'], stdout=PIPE, stderr=DEVNULL)
    p.communicate()

def kill_network():
	Popen(['killall', 'network-manager', 'wpa_supplicant', 'hostapd dnsmasq'],stdout=DEVNULL, stderr=DEVNULL).communicate()


def nat(out, masuk):
	execute_commands([
		'iptables --table nat --append POSTROUTING --out-interface ' +out+ ' -j MASQUERADE',
		'iptables --append FORWARD --in-interface ' +masuk+ ' --out-interface ' +out+ ' -j ACCEPT'
    ])

def reset():
    ls = os.listdir("config")
    if "dnsmasq.conf" in ls:
        os.remove("dnsmasq.conf")
    if "hostapd.conf" in ls:
        os.remove("hostapd.conf")
        
def redirect_localhost():

	execute_commands([
		"iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT "
		"--to-destination 10.0.0.1:80",
		"iptables -t nat -A PREROUTING -p udp --dport 53 -j DNAT "
		"--to-destination 10.0.0.1:80",
		"iptables -t nat -A PREROUTING -p tcp --dport 53 -j DNAT "
		"--to-destination 10.0.0.1:80",
		"iptables -t nat -A PREROUTING -p tcp --dport 443 -j DNAT "
		"--to-destination 10.0.0.1:80"
	])
	
def clear_rules():
	execute_commands([
		"iptables -F", "iptables -X", "iptables -t nat -F",
		"iptables -t nat -X"
	])

def check_port(port):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	result = sock.connect_ex(('127.0.0.1',port))
	if result == 0:
		warn("Failed to listen on port {} (reason: Address already in use)".format(port))
		sock.close()
		exit()
	sock.close()
