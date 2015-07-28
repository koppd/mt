#!/usr/bin/python

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
                   build=False,
                   autoSetMacs=True,
                   ipBase='10.0.0.0/8')
    #net.staticArp()
    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
#    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    r2 = net.addHost('r2', cls=Node, ip='0.0.0.0')
    r2.cmd('sysctl -w net.ipv4.ip_forward=1')
#    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
    r4 = net.addHost('r4', cls=Node, ip='0.0.0.0')
    r4.cmd('sysctl -w net.ipv4.ip_forward=1')
#    s5 = net.addSwitch('s5', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.1.0.100/24', defaultRoute='via 10.1.0.1')
    h2 = net.addHost('h2', cls=Host, ip='10.3.0.100/24', defaultRoute='via 10.3.0.1')

    info( '*** Add links\n')
#    net.addLink(s1, h1)
#    net.addLink(r2, s1)
#    net.addLink(s3, r2)
#    net.addLink(r4, s3)
#    net.addLink(s5, r4)
#    net.addLink(s5, h2)

    net.addLink(r2, h1)
    net.addLink(r4, r2)
    net.addLink(h2, r4)


    info( '*** Starting network\n')
    net.build()

    r2.setIP('10.1.0.1', prefixLen = 24, intf = 'r2-eth0')

    r2.setIP('10.2.0.1', prefixLen = 24, intf = 'r2-eth1')
    r4.setIP('10.2.0.2', prefixLen = 24, intf = 'r4-eth0')

    r4.setIP('10.3.0.1', prefixLen = 24, intf = 'r4-eth1')

    r4.cmd('ip route add 10.1.0.0/24 via 10.2.0.1')
    r2.cmd('ip route add 10.3.0.0/24 via 10.2.0.2')
    
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
#    net.get('s1').start([])
#    net.get('s3').start([])
#    net.get('s5').start([])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

