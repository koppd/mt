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

from mininet.term import makeTerm, makeTerms, runX11, tunnelX11, cleanUpScreens
import shlex, subprocess
#import mininet.term
import time
import os
import signal
#from subprocess import call

class netTCPloss():

    def myNetwork( self, delay=20, loss=5, swin=3 ):
    
        self.net = Mininet( topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')
                       #xterms = True)
    
    #    info( '*** Adding controller\n' )
        info( '*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    
    #    info( '*** Add hosts\n')
        self.h1 = self.net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    ##    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    ##    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
        self.h4 = self.net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    
        info( '*** Add links\n')
    #    h1s1_delay = str(delay) + 'ms'
        self.h1s1 = {'delay':str(delay) + 'ms','loss':0,'max_queue_size':swin}
        self.net.addLink(self.h1, self.s1, cls=TCLink , **self.h1s1)
    ##    h2s1 = {'delay':'500ms','loss':5}
    ##    net.addLink(h2, s1, cls=TCLink , **h2s1)
    ##    h3s1 = {'delay':'250ms','loss':5}
    ##    net.addLink(h3, s1, cls=TCLink , **h3s1)
        self.h4s1 = {'delay':str(delay) + 'ms','loss':loss}
        self.net.addLink(self.h4, self.s1, cls=TCLink , **self.h4s1)
    
        info( '\n*** Starting network\n')
        self.net.build()
    #    info( '*** Starting controllers\n')
        for self.controller in self.net.controllers:
            self.controller.start()
    
    #    info( '*** Starting switches\n')
        self.net.get('s1').start([])
    
    #    info( '\n*** Post configure switches and hosts\n')
    
    # starte httpServer auf h1
        info( '\n****** execute startHTTPserver on h4\n')
        self.http = self.h1.cmd("python -m SimpleHTTPServer 80 &", printPid=True)
        print "http ", self.http
    
    # starte wireshark auf h4    
        info( '****** execute wireshark on h4\n')
        self.display, self.tunnel = tunnelX11( self.h4, None )
    #    ws = h4.popen( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1'], shell=True)
        self.ws = self.h4.cmd( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1 &'], shell=True, printPid=True) #, preexec_fn=os.setsid )
        print "ws ", self.ws
    
    # oeffne xterm auf h4
#        self.hostref = makeTerm( self.h4, "starte TCP Verbindung..." )   #<<< geht
#    
#        info( '\n')
#        info( '***************************\n')
#        info( '****** Anleitung **********\n')
#        print "Geben Sie folgenden Befehl im xterm Fenster ein:"
#        print "wget -O /dev/null 10.0.0.1/smallfile"
#        info( '***************************\n')
            
    
#        CLI(net)
        
    #    ws.kill()
    #    http.kill()
        
        #print "gucke ob HTTP noch laeuft", http
        #print "gucke ob'wireshark noch laeuft", ws
        
    #    h4.terminate()
    #    h1.terminate()
        #print os.killpg(ws.pid, signal.SIGTERM)
        
#        cleanUpScreens()   #beendet alle xterm und wireshark Fenster
        
#        net.stop()


    def startDownload( self ):    
        display, tunnel = tunnelX11( self.h4, None )
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        self.p1 = self.h4.popen( ['xterm', '-title', 'Download_in_progress...', '-display ' + display, '-e', 'env TERM=ansi wget -O /dev/null 10.0.0.1/smallfile'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
       
    
    def stopNet( self ):
        self.h4.cmd("pkill wireshark")
        # simpleHTTP muss auch beendet werden. Steht in self.http drinnen.
        # muss evtl. generisch über ps -aux |grep SimpleHTTPServer beendet werden.
        self.net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    tmp = netTCPloss()
    tmp.myNetwork()
    info( 'ich warte noch 5 Sekunden...\n')
    time.sleep(5000)
    tmp.startDownload()

