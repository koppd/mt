#!/usr/bin/python

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

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')
                   #xterms = True)

#    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

#    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
##    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
##    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(h1, s1)
##    h2s1 = {'delay':'500ms','loss':5}
##    net.addLink(h2, s1, cls=TCLink , **h2s1)
##    h3s1 = {'delay':'250ms','loss':5}
##    net.addLink(h3, s1, cls=TCLink , **h3s1)
    h4s1 = {'delay':'250ms','loss':1}
    net.addLink(h4, s1, cls=TCLink , **h4s1)

    info( '\n*** Starting network\n')
    net.build()
#    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

#    info( '*** Starting switches\n')
    net.get('s1').start([])

#    info( '\n*** Post configure switches and hosts\n')

# starte httpServer auf h1
    info( '\n****** execute startHTTPserver on h4\n')
    http = h1.cmd("python -m SimpleHTTPServer 80 &", printPid=True)
    print "http ", http

# starte wireshark auf h4    
    info( '****** execute wireshark on h4\n')
    display, tunnel = tunnelX11( h4, None )
#    ws = h4.popen( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1'], shell=True)
    ws = h4.cmd( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1 &'], shell=True, printPid=True) #, preexec_fn=os.setsid )
    print "ws ", ws

# oeffne xterm auf h4
    hostref = makeTerm( h4, "starte TCP Verbindung..." )   #<<< geht

    info( '\n')
    info( '***************************\n')
    info( '****** Anleitung **********\n')
    print "Geben Sie folgenden Befehl im xterm Fenster ein:"
    print "wget -O /dev/null 10.0.0.1/bigfile"
    info( '***************************\n')
        

    CLI(net)
    
#    ws.kill()
#    http.kill()
    
    print "gucke ob HTTP noch laeuft", http
    print "gucke ob'wireshark noch laeuft", ws
    
#    h4.terminate()
#    h1.terminate()
    #print os.killpg(ws.pid, signal.SIGTERM)
    
    cleanUpScreens()   #beendet alle xterm und wireshark Fenster
    
    net.stop()
    

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

