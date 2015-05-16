#!/usr/bin/python
# -*- coding: utf-8 -*-

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call


def myNetwork():

    net = Mininet( topo=None,
                   build=False)
#                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
#    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
#    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, defaultRoute=None)

    host_h1 =  net.getNodeByName('h1')

    info( '*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    print "ip1 of host h1: ", h1.IP()

    info( '*** Starting network\n')
#    net.build()
# versuche es manuell: (ich wollte wissen, wann ein Link/Interface
# eine IP Adresse bekommt.)
    info( '*** Configuring hosts\n' )

    info( h1.name + ' \n' )
    intf = h1.defaultIntf()
    print "ip2a of host h1: ", h1.IP()   #"IP: None"
    if intf:
        h1.configDefault()
        print "ip2b of host h1: ", h1.IP()  #"IP: 10.0.0.1"
    else:
        # Don't configure nonexistent intf
        h1.configDefault( ip=None, mac=None )
        print "ip2c of host h1: ", h1.IP()
    info( '\n' )
    h1.built = True

# versuche es manuell:
    info( h2.name + ' \n' )
    intf = h2.defaultIntf()
    if intf:
        h2.configDefault()
    else:
        # Don't configure nonexistent intf
        h2.configDefault( ip=None, mac=None )
    info( '\n' )
    h2.built = True



    print "ip2 of host h1: ", h1.IP()

    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    print "ip3 of host h1: ", h1.IP()

    info( '*** Starting switches\n')
    net.get('s1').start([])

    print "ip4 of host h1: ", host_h1.IP()

    info( '*** Post configure switches and hosts\n')

#extra Links, diese haben als Interface: h1-eth1
#IP Adresse dafue ist: None.
    net.addLink(h1, s1)
    net.addLink(h2, s1)
# mit dhclient -d -v h2-eth1 werden auf h2 DHCP Discover Nachrichten verschickt. (UDP)
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

