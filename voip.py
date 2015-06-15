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

from mininet.term import makeTerm, makeTerms, runX11, tunnelX11, cleanUpScreens

import time

class netVoIP():

    def myNetwork(self, delay = 20 ):
    
        self.net = Mininet( topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')
    
        info( '*** Adding controller\n' )
        info( '*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    
        info( '*** Add hosts\n')
        self.h1 = self.net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        self.h2 = self.net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
        self.h3 = self.net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    
        info( '*** Add links\n')
        self.h1s1 = {'delay':str(delay) + 'ms'}
        self.net.addLink(self.h1, self.s1, cls=TCLink , **self.h1s1)
        self.h2s1 = {'delay':str(delay) + 'ms'}
        self.net.addLink(self.h2, self.s1, cls=TCLink , **self.h2s1)
        self.h3s1 = {'delay':str(delay) + 'ms'}
        self.net.addLink(self.h3, self.s1, cls=TCLink , **self.h3s1)

#        self.net.addLink(self.h1, self.s1)
#        self.net.addLink(self.h2, self.s1)
#        self.net.addLink(self.h3, self.s1)
    
        info( '*** Starting network\n')
        self.net.build()
        info( '*** Starting controllers\n')
        for self.controller in self.net.controllers:
            self.controller.start()
    
        info( '*** Starting switches\n')
        self.net.get('s1').start([])
    
        info( '*** Post configure switches and hosts\n')
    
    # starte wireshark auf h2   
        info( '****** execute wireshark on h1\n')
        display, tunnel = tunnelX11( self.h1, None )
    #    ws = h4.popen( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1'], shell=True)
        self.ws = self.h1.cmd( ['wireshark -i h1-eth0 -k -Y "sip || rtp" &'], shell=True, printPid=True)
        print "pid wireshark: ", self.ws

    # starte asterisk
        self.asterisk = self.h1.cmd( ['asterisk'], shell=True, printPid=True)
        print "pid wireshark: ", self.asterisk
        


    def startPhones( self ):

    # starte linphone
        display, tunnel = tunnelX11( self.h2, None )
        self.linphone = self.h2.cmd( ['linphone &'], shell=True, printPid=True)
        print "pid linphone: ", self.linphone

#        time.sleep(0.5)

    # starte ekiga
        display, tunnel = tunnelX11( self.h3, None )
        self.ekiga = self.h3.cmd( ['ekiga &'], shell=True, printPid=True)
        print "pid ekiga: ", self.ekiga
        
#        CLI(self.net)
#        net.stop()

    def enterCLI ( self ):
        CLI(self.net)

    def stopNet( self ):
#        cleanUpScreens() 
        self.h1.cmd("pkill ekiga")
        self.h2.cmd("pkill linphone")
        self.h2.cmd("pkill asterisk")
        self.net.stop()
#        print("Button VoIPExit pressed")


if __name__ == '__main__':
    setLogLevel( 'info' )
    tmp = netVoIP()
    tmp.myNetwork()
    tmp.startPhones()
    tmp.enterCLI()
    tmp.stopNet()

