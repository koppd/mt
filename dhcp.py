#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 02:04:12 2015

@author: mininet

File dhcpd_mn.conf has to be copied into /etc/dhcp/
it's not possible to use any other directory for the dhcpd program than 
/etc/dhcp (even with option -cf) because AppArmor would not accept it.
It will resure any access with an "access denied".
Sol 1: disable AppArmor or create exceptions
Sol 2: copy the .conf file automatically (implemented)

ToDO:
fixed MAC
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf

from mininet.term import makeTerm, makeTerms, runX11, tunnelX11, cleanUpScreens
import shlex, subprocess
#import mininet.term
import time
import os
import signal
#from subprocess import call

def myNetwork( delay = 20, 
              fresh_daemon_leases = True, 
              fresh_client_leases = True,
              MAC_random = True ):
    if MAC_random == True:
        net = Mininet( topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')
                       #xterms = True)
    else:
        net = Mininet( topo=None,
                       build=False,
                       autoSetMacs=True,
                       ipBase='10.0.0.0/8')
                       #xterms = True)
        

#    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

#    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    info( '*** Add links\n')
#    h1s1_delay = str(delay) + 'ms'
    h1s1 = {'delay':str(delay) + 'ms'}
    net.addLink(h1, s1, cls=TCLink , **h1s1)
    h2s1 = {'delay':str(delay) + 'ms'}
    net.addLink(h2, s1, cls=TCLink , **h2s1)
##    h3s1 = {'delay':'250ms','loss':5}
##    net.addLink(h3, s1, cls=TCLink , **h3s1)
##    h4s1 = {'delay':str(delay) + 'ms','loss':loss}
##    net.addLink(h4, s1, cls=TCLink , **h4s1)

    info( '\n*** Starting network\n')
    net.build()
#    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

#    info( '*** Starting switches\n')
    net.get('s1').start([])

#    info( '\n*** Post configure switches and hosts\n')

# starte DHCP-Server auf h1
    info( '\n****** execute DHCP server on h1\n')
    print "copy configuration file to /etc/dhcp/dhcpd_mn.conf"
    h1.cmd("cp ./dhcpd_mn.conf /etc/dhcp/", printPid=True)
    if fresh_daemon_leases == True:
        print "delete /var/lib/dhcp/dhcpd.leases.mn"
        h1.cmd("rm /var/lib/dhcp/dhcpd.leases.mn", printPid=True)
        h1.cmd("touch /var/lib/dhcp/dhcpd.leases.mn", printPid=True)
    else:
        print "verwende vorhandene /var/lib/dhcp/dhcpd.leases.mn"
    
    h1.cmd("ifconfig h1-eth0 192.168.2.1", printPid=True)
    dhcp = h1.cmd("dhcpd -d -cf /etc/dhcp/dhcpd_mn.conf  -lf /var/lib/dhcp/dhcpd.leases.mn h1-eth0 &", printPid=True)
    print "pid dhcp: ", dhcp

    if fresh_client_leases == True:
        print "delete /var/lib/dhcp/dhclient.leases.mn"
        h2.cmd("rm /var/lib/dhcp/dhclient.leases.mn", printPid=True)
        h2.cmd("touch /var/lib/dhcp/dhclient.leases.mn", printPid=True)
    else:
        print "verwende vorhandene /var/lib/dhcp/dhclient.leases.mn"
        h2.cmd("touch /var/lib/dhcp/dhclient.leases.mn", printPid=True)
        

# starte wireshark auf h2   
    info( '****** execute wireshark on h2\n')
    display, tunnel = tunnelX11( h2, None )
#    ws = h4.popen( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1'], shell=True)
    ws = h2.cmd( ['wireshark -i h2-eth0 -k -Y bootp.dhcp==1 &'], shell=True, printPid=True) #, preexec_fn=os.setsid )
    print "pid wireshark: ", ws

# oeffne xterm auf h2
    hostref = makeTerm( h2, "start DHCP Client..." )   #<<< geht

    info( '\n')
    info( '***************************\n')
    info( '****** Anleitung **********\n')
    print "Geben Sie folgenden Befehl im xterm Fenster ein:"
    print "dhclient -d -v -lf /var/lib/dhcp/dhclient.leases.mn h2-eth0"
    info( '***************************\n')
        

    CLI(net)

    h1.cmd("pkill dhcpd")
    
#    ws.kill()
#    http.kill()
    
    #print "gucke ob HTTP noch laeuft", http
    #print "gucke ob'wireshark noch laeuft", ws
    
#    h4.terminate()
#    h1.terminate()
    #print os.killpg(ws.pid, signal.SIGTERM)
    
    cleanUpScreens()   #beendet alle xterm und wireshark Fenster
    
    net.stop()
    

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
