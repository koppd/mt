#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 2015-05-27

@author: Dominik Kopp

Description:


ToDO:


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
from socket import *

#from subprocess import call

class netFTP():

    def myNetwork( self, delay=20, anon=False ):
        self.net = Mininet( topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')
                       #xterms = True)
    
    #    info( '*** Adding controller\n' )
        info( '*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    
    #    info( '*** Add hosts\n')
        self.h1 = self.net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        self.h2 = self.net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    
        info( '*** Add links\n')
    #    h1s1_delay = str(delay) + 'ms'
        self.h1s1 = {'delay':str(delay) + 'ms'}
        self.net.addLink(self.h1, self.s1, cls=TCLink , **self.h1s1)
        self.h2s1 = {'delay':str(delay) + 'ms'}
        self.net.addLink(self.h2, self.s1, cls=TCLink , **self.h2s1)
    
        info( '\n*** Starting network\n')
        self.net.build()
    #    info( '*** Starting controllers\n')
        for self.controller in self.net.controllers:
            self.controller.start()
    
    #    info( '*** Starting switches\n')
        self.net.get('s1').start([])
    
    #    info( '\n*** Post configure switches and hosts\n')
    
    # starte wireshark auf h2   
        info( '****** execute wireshark on h2\n')
        display, tunnel = tunnelX11( self.h2, None )
    #    ws = h4.popen( ['wireshark -i h4-eth0 -k -Y ip.addr==10.0.0.1'], shell=True)
        self.ws = self.h2.cmd( ['wireshark -i h2-eth0 -k -Y "ftp || ftp-data" &'], shell=True, printPid=True) #, preexec_fn=os.setsid )
        print "pid wireshark: ", self.ws

    # starte ftpServer auf h1
        self.vsftp = self.h1.cmd( ['vsftpd &'], shell=True, printPid=True) #, preexec_fn=os.setsid )
        print "pid vsftpd: ", self.vsftp


    def connect( self, host, port):
        """connect to the server
            params:
                host: the server host
                port: the server port (normally 110)
            returns: a socket that is connected to the server
        """
        clientSocket = socket(AF_INET, SOCK_STREAM)
        print "Verbdungsaufbau... ", host, int(port)
        clientSocket.connect((host, int(port)))
        # FIXME hier das OK pruefen
        
        print "warte auf Begruessungsnachricht..."
        toRecv = clientSocket.recv(1024)
        toRecv = toRecv.decode(encoding='UTF-8')
        print "empfangen nach connect:", toRecv
        
        return clientSocket
    
    def send_user( self, clientSocket, user):
        """ send the USER command """
    
        toSend = bytes("USER " + user + "\r\n", encoding="utf-8")
        clientSocket.send(toSend)
    
        toRecv = clientSocket.recv(1024)
        toRecv = toRecv.decode(encoding='UTF-8')
        print "empfangen nach USER:", toRecv
        # FIXME hier das OK pruefen
        if toRecv == "+OK\r\n":
            return 0
        else:
            return 1
    
    def send_pass( self, clientSocket, password):
        """ send the PASS command """
        
        toSend = "PASS " + password + "\r\n"
        clientSocket.send(bytes(toSend, encoding="utf-8"))
    
        toRecv = clientSocket.recv(1024)
        # FIXME hier das OK pruefen
        print "empfangen nach PASS:", toRecv
        toRecv = toRecv.decode(encoding='UTF-8')
        
        return 0


    def send_cwd( self, clientSocket, directory):
        """ send the CWD command """
        
        toSend = "CWD " + directory + "\r\n"
        clientSocket.send(bytes(toSend, encoding="utf-8"))
    
        toRecv = clientSocket.recv(1024)
        # FIXME hier das OK pruefen
        print "empfangen nach CWD:", toRecv
        toRecv = toRecv.decode(encoding='UTF-8')
        
        return 0


    def send_retr( self, clientSocket, filename):
        """ send the RETR command """
        pass
    

    def close_connection( self, clientSocket):
        """ close the connection """
    
        clientSocket.send(b"QUIT\r\n")
        toRecv = clientSocket.recv(1024)
        # FIXME hier das OK pruefen
        print "empfangen nach QUIT:", toRecv 
        clientSocket.close()

    
    def startDownload( self ):    
#        display, tunnel = tunnelX11( self.h2, None )
##        self.p1 = self.h2.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
#        self.p1 = self.h2.popen( ['xterm', '-title', 'Download_in_progress...', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


 
        if 1==2:
            CLI(self.net)
        else:
# Erzeuge Socket
            print "create socket..."
            clientSocket = self.connect(self.h1.IP(), 21)

# Verbinde mit FTP-Server

# sende Username
            self.send_user(clientSocket, "mininet")

# sende Passwort
            self.send_pass(clientSocket, "mininet")

# wechsle Verzeichnis
            self.send_cwd(clientSocket, "mininet")
            self.send_cwd(clientSocket, "demo")

# Download Datei
#           send_retr(clientSocket, "ftp_downloadfile")


# Verabschieden und beende Verbindung
            self.send_quit(clientSocket)
            self.close_connection(clientSocket)
       
    
    def stopNet( self ):
        self.h2.cmd("pkill wireshark")
        # simpleHTTP muss auch beendet werden. Steht in self.http drinnen.
        # muss evtl. generisch über ps -aux |grep SimpleHTTPServer beendet werden.
        self.net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    tmp = netFTP()
    tmp.myNetwork()
    info( 'ich warte noch 5 Sekunden...\n')
    time.sleep(5000)
    tmp.startDownload()
