#-*- coding: utf-8 -*-
import sys
#from PySide import QtGui
#from PySide import QtCore
from PyQt4 import QtGui, QtCore
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import uic
#import TCPloss

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

#from mainwindow import Ui_MainWindow

class MN():
    def startMN(self, MAC_random = True):
        self.createNet(MAC_random)
        self.createSwitch()
        self.createRouters()
        self.createHosts()
        self.initLinkvalues()
        self.createLinks()
        self.createRoutes()
        self.buildNet()
        self.startController()
        self.startSwitch()

    def getIP(self, host):
        tmphost = self.getNode( host )   #e.g. host = h1
        try:
            return tmphost.IP()
        except:
            print "kein entsprechenden MN Host-IP gefunden"
            return None
        return None

    def getMAC(self, host):
        tmphost = self.getNode( host )   #e.g. host = h1
        try:
            return tmphost.MAC()
        except:
            print "kein entsprechenden MN Host-MAC gefunden"
            return None
        return None

    def getNode(self, host):
        info( '*** host type\n' + str(type(host)) + '\n')
        info( '*** host details\n' + str(host) + '\n')

        try:
            info( '*** host getNodeByName\n' + str(self.net.getNodeByName( host )) + '\n')

            return self.net.getNodeByName( host )   #e.g. host = h1
        except:
            print "Node %s existiert nicht" % host
            return None


    def createNet(self, MAC_random = True):
        if MAC_random == True:
            self.net = Mininet( topo=None,
                           build=False,
                           ipBase='10.0.0.0/8')
        else:
            self.net = Mininet( topo=None,
                           build=False,
                           autoSetMacs=True,
                           ipBase='10.0.0.0/8')

    def createSwitch(self):
        info( '*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
        self.s2 = self.net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')

    def createRouters(self):
        pass
        self.r1 = self.net.addHost(mySW.shortcut.GUIrouter['Router01'], cls=Host, ip='10.0.0.100/24')
        self.r2 = self.net.addHost(mySW.shortcut.GUIrouter['Router02'], cls=Host, ip='10.0.1.22/29')
        self.r3 = self.net.addHost(mySW.shortcut.GUIrouter['Router03'], cls=Node, ip='10.0.1.33/29')
        self.r4 = self.net.addHost(mySW.shortcut.GUIrouter['Router04'], cls=Node, ip='10.0.1.42/29')
        self.r1.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r2.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r3.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    def createHosts(self):
        self.h1 = self.net.addHost(mySW.shortcut.GUIhosts['Host01'], cls=Host, ip='10.0.0.1/24', defaultRoute='via 10.0.0.100')
        self.h2 = self.net.addHost(mySW.shortcut.GUIhosts['Host02'], cls=Host, ip='10.0.0.2/24', defaultRoute='via 10.0.0.100')
        self.h3 = self.net.addHost(mySW.shortcut.GUIhosts['Host03'], cls=Host, ip='10.0.0.3/24', defaultRoute='via 10.0.0.100')
        self.h4 = self.net.addHost(mySW.shortcut.GUIhosts['Host04'], cls=Host, ip='10.0.1.17/29', defaultRoute='via 10.0.1.22')
        self.h5 = self.net.addHost(mySW.shortcut.GUIhosts['Host05'], cls=Host, ip='10.0.1.34/29', defaultRoute='via 10.0.1.33')
        self.h6 = self.net.addHost(mySW.shortcut.GUIhosts['Host06'], cls=Host, ip='10.0.1.35/29', defaultRoute='via 10.0.1.33')
        info( '*** h1 details\n' + str(self.h1) + '\n')
        info( '*** h1 details\n' + str(type(self.h1)) + '\n')
#        info( '*** h1 details\n' + str(self.h1.IP()) + '\n')
#        info( '*** h1 IP\n' + str(self.net.getNodeByName( self.h1 ) ) + '\n')


    def initLinkvalues(self):
        self.defaultDelay = 5
        self.h1s1 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}
        self.h2s1 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}
        self.h3s1 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}
        self.h4s1 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}
        self.h5s2 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}
        self.h6s2 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}

# Router fehlen noch
#        self.h4r2 = {'delay':str(defaultDelay) + 'ms','loss':0,'max_queue_size':swin}
#        self.h5r3 = {'delay':str(defaultDelay) + 'ms','loss':0,'max_queue_size':swin}
#        self.h6r3 = {'delay':str(defaultDelay) + 'ms','loss':0,'max_queue_size':swin}

    def createLinks(self):
# Beispiel für delay
#        self.h1s1 = {'delay':str(self.defaultDelay) + 'ms'}
#        self.h1s1 = {'delay':str(defaultDelay) + 'ms','loss':0,'max_queue_size':swin}
        self.net.addLink(self.h1, self.s1, cls=TCLink , **self.h1s1)
        self.net.addLink(self.h2, self.s1, cls=TCLink , **self.h2s1)
        self.net.addLink(self.h3, self.s1, cls=TCLink , **self.h3s1)

        self.net.addLink(self.s1, self.r1, cls=TCLink)
        self.r1.setIP('10.0.0.100', prefixLen = 24, intf = 'r1-eth0')
        self.net.addLink(self.h4, self.r2, cls=TCLink)

        self.net.addLink(self.h5, self.s2, cls=TCLink , **self.h5s2)
        self.net.addLink(self.h6, self.s2, cls=TCLink , **self.h6s2)
        self.net.addLink(self.s2, self.r3, cls=TCLink)

        self.net.addLink(self.r1, self.r2, cls=TCLink)
        self.r1.setIP('10.0.1.9', prefixLen = 29, intf = 'r1-eth1')
        self.r2.setIP('10.0.1.10', prefixLen = 29, intf = 'r2-eth1')

        self.net.addLink( self.r2, self.r3, intfName2='r3-eth1', params2={ 'ip' : '10.0.1.26/29' } )
        self.r2.setIP('10.0.1.25', prefixLen = 29, intf = 'r2-eth2')
#        self.r3.setIP('10.0.1.26', prefixLen = 29, intf = 'r3-eth1')


        self.net.addLink( self.r3, self.r4, intfName2='r4-eth0', params2={ 'ip' : '10.0.1.42/29' } ) #doppel zu oben
        self.r3.setIP('10.0.1.41', prefixLen = 29, intf = 'r3-eth2')
#        self.r4.setIP('10.0.1.42', prefixLen = 29, intf = 'r4-eth0')  

        self.net.addLink( self.r1, self.r4, intfName2='r4-eth1', params2={ 'ip' : '10.0.1.49/29' } )
#        self.r4.setIP('10.0.1.49', prefixLen = 29, intf = 'r4-eth2')
        self.r1.setIP('10.0.1.50', prefixLen = 29, intf = 'r1-eth2')

        self.net.addLink( self.r2, self.r4, intfName2='r4-eth2', params2={ 'ip' : '10.0.1.58/29' } )
        self.r2.setIP('10.0.1.57', prefixLen = 29, intf = 'r2-eth3')
#        self.r4.setIP('10.0.1.58', prefixLen = 29, intf = 'r4-eth3')

    def createRoutes(self):

        self.r1.cmd('ip route add 10.0.1.16/29 via 10.0.1.10') #C
        self.r1.cmd('ip route add 10.0.1.24/29 via 10.0.1.10') #D
        self.r1.cmd('ip route add 10.0.1.32/29 via 10.0.1.10') #E
        self.r1.cmd('ip route add 10.0.1.40/29 via 10.0.1.49') #F
        self.r1.cmd('ip route add 10.0.1.56/29 via 10.0.1.49') #H

        self.r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.9') #A
        self.r2.cmd('ip route add 10.0.1.32/29 via 10.0.1.26') #E
        self.r2.cmd('ip route add 10.0.1.40/29 via 10.0.1.58') #F
        self.r2.cmd('ip route add 10.0.1.48/29 via 10.0.1.58') #G

        self.r3.cmd('ip route add 10.0.1.16/29 via 10.0.1.25') #C
        self.r3.cmd('ip route add 10.0.1.56/29 via 10.0.1.42') #H
        self.r3.cmd('ip route add 10.0.1.8/29 via 10.0.1.25') #B
        self.r3.cmd('ip route add 10.0.1.48/29 via 10.0.1.42') #G
        self.r3.cmd('ip route add 10.0.0.0/24 via 10.0.1.25') #A

        self.r4.cmd('ip route add 10.0.0.0/24 via 10.0.1.50') #A
        self.r4.cmd('ip route add 10.0.1.8/29 via 10.0.1.50') #B
        self.r4.cmd('ip route add 10.0.1.16/29 via 10.0.1.57') #C
        self.r4.cmd('ip route add 10.0.1.24/29 via 10.0.1.41') #D
        self.r4.cmd('ip route add 10.0.1.32/29 via 10.0.1.41') #E


    def modifyLink(self):
        pass

    def buildNet(self):
        self.net.build()

    def startController(self):
        info( '*** Starting controllers\n')
        for self.controller in self.net.controllers:
            self.controller.start()

    def startSwitch(self):
        info( '*** Starting switches\n')
        self.net.get('s1').start([])
        self.net.get('s2').start([])

        info( '*** h1 details2\n' + str(self.h1) + '\n')
        info( '*** h1 details2\n' + str(type(self.h1)) + '\n')
        info( '*** h1 details2\n' + str(self.h1.IP()) + '\n')

    def startCLI(self):
        CLI( self.net )

    def stopNet( self ):
        self.h1.cmd("pkill dhcpd")
        self.h1.cmd("pkill asterisk")
        self.h1.cmd("pkill vsftp")
        self.net.stop()

    def sendCmd( self, node, command ):
        return node.cmd(command, shell=True, printPid=True)


class MNtcp():
    def myNetwork( self, delay=20, loss=5, swin=3 ):

        self.net = Mininet( topo=None,
                       build=False,
                       ipBase='10.0.0.0/8')

        info( '*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')

    #    info( '*** Add hosts\n')
        self.h1 = self.net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        self.h4 = self.net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)

        info( '*** Add links\n')
    #    h1s1_delay = str(delay) + 'ms'
        self.h1s1 = {'delay':str(delay) + 'ms','loss':0,'max_queue_size':swin}
        self.net.addLink(self.h1, self.s1, cls=TCLink , **self.h1s1)
        self.h4s1 = {'delay':str(delay) + 'ms','loss':loss}
        self.net.addLink(self.h4, self.s1, cls=TCLink , **self.h4s1)

        info( '\n*** Starting network\n')
        self.net.build()

        for self.controller in self.net.controllers:
            self.controller.start()

        self.net.get('s1').start([])

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


    def startDownload( self ):
        display, tunnel = tunnelX11( self.h4, None )
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        self.p1 = self.h4.popen( ['xterm', '-title', 'Download_in_progress...', '-display ' + display, '-e', 'env TERM=ansi wget -O /dev/null 10.0.0.1/smallfile'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


    def stopNet( self ):
        self.h4.cmd("pkill wireshark")
        # simpleHTTP muss auch beendet werden. Steht in self.http drinnen.
        # muss evtl. generisch über ps -aux |grep SimpleHTTPServer beendet werden.
        self.net.stop()

class Services():
    def __init__(self):
        self.DHCPnode = None
        self.HTTPnode = None
        self.VSFTPnode = None
        self.VOIPnode = None
        print "Klasse Services aufgerufen"

    def setDHCP(self, MNnode):
        self.DHCPnode = MNnode
        print "DHCPnode gesetzt:", self.DHCPnode

    def getDHCPip(self):
        if self.DHCPnode != None:
            return self.DHCPnode.IP()

    def getDHCPguiHost(self):
        if self.DHCPnode != None:
            return mySW.shortcut.getGUIname(self.DHCPnode)

    def isDHCP(self):
        print "isDHCP", self.DHCPnode
        if self.DHCPnode != None:
            return True
        else:
            return False


    def setVSFTP(self, MNnode):
        self.VSFTPnode = MNnode

    def getVSFTPip(self):
        if self.VSFTPnode != None:
            return self.VSFTPnode.IP()

    def getVSFTPguiHost(self):
        if self.VSFTPnode != None:
            return mySW.shortcut.getGUIname(self.VSFTPnode)

    def isVSFTP(self):
        if self.VSFTPnode != None:
            return True
        else:
            return False


    def setVOIP(self, MNnode):
        self.VOIPnode = MNnode

    def getVOIPip(self):
        if self.VOIPnode != None:
            return self.VOIPnode.IP()

    def getVOIPguiHost(self):
        if self.VOIPnode != None:
            return mySW.shortcut.getGUIname(self.VOIPnode)

    def isVOIP(self):
        if self.VOIPnode != None:
            return True
        else:
            return False


    def setHTTP(self, MNnode):
        self.HTTPnode = MNnode

    def getHTTPip(self):
        if self.HTTPnode != None:
            return self.HTTPnode.IP()

    def getHTTPguiHost(self):
        if self.HTTPnode != None:
            return mySW.shortcut.getGUIname(self.HTTPnode)

    def isHTTP(self):
        if self.HTTPnode != None:
            return True
        else:
            return False



class HostConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(HostConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confHost.ui', self)
#        print "hostconfig init...)"
        info( '\n****** erzeuge liste \n')
        for host in mySW.getNodeList("Host"):
            self.listHost.addItem(QListWidgetItem(host.objectName()))
        info( '\n****** hostliste erzeugt\n')
#old style
#        self.connect(self.buttonBox.button(QDialogButtonBox.Reset), QtCore.SIGNAL("clicked()"), self.resetButton)
#        self.connect(self.buttonBox.button(QDialogButtonBox.Apply), QtCore.SIGNAL("clicked()"), self.applyButton)
#new style
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetButton)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.applyButton)

        self.listHost.currentItemChanged.connect(self.currentHostChanged)
        self.pbXterm.clicked.connect(self.pbXtermclicked)
#Server tab
        self.pbSDHCP.clicked.connect(self.pbSDHCPclicked)
        self.pbSWireshark.clicked.connect(self.pbSWiresharkclicked)
#Client tab
        self.pbCFTP.clicked.connect(self.pbCFTPclicked)
        self.pbCWireshark.clicked.connect(self.pbCWiresharkclicked)

    def applyButton(self):
#        print "apply buttton"
        self.applyChanges()

    def resetButton(self):
#        print "reset buttton"
        pass

    def accept(self):
#        print "accept/OK button"
        self.applyChanges()
        QDialog.accept(self)

#        self.close()

    def reject1_not_used(self):
        print "reject"
#        self.close()
        #QDialog.reject()


    def startSimpleHTTPserver(self, MNnode):
        info( '\n****** execute startHTTPserver on %s\n' % MNnode.name) #selectedHostText)
        pid = mySW.instanceMN.sendCmd(MNnode, "python -m SimpleHTTPServer 80 &")
        print "pid http:", pid

        mySW.services.setHTTP(MNnode)

        return pid

    def startVSFTP(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'vsftpd &') #, preexec_fn=os.setsid )
        print "pid vsftpd:", pid

        mySW.services.setVSFTP(MNnode)
        return pid

    def startDHCPD(self, MNnode, fresh_daemon_leases = True):
        info( '\n****** execute DHCP server on %s\n' % MNnode.name)
        print "copy configuration file to /etc/dhcp/dhcpd_mn.conf"
        MNnode.cmd("cp ./dhcpd_mn.conf /etc/dhcp/", printPid=True)
        if fresh_daemon_leases == True:
            print "delete /var/lib/dhcp/dhcpd.leases.mn"
            MNnode.cmd("rm /var/lib/dhcp/dhcpd.leases.mn", printPid=True)
            MNnode.cmd("touch /var/lib/dhcp/dhcpd.leases.mn", printPid=True)
        else:
            print "verwende vorhandene /var/lib/dhcp/dhcpd.leases.mn"
#FIXME
        MNnode.cmd("ifconfig %s-eth0 192.168.2.1" % MNnode.name, printPid=True)
        pid = MNnode.cmd("dhcpd -d -cf /etc/dhcp/dhcpd_mn.conf  -lf /var/lib/dhcp/dhcpd.leases.mn %s-eth0 &" % MNnode.name, printPid=True)
        print "pid dhcp: ", pid

        mySW.services.setDHCP(MNnode)
        return pid

    def startDownload(self, MNnode):
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
#            self.p1 = MNnode.popen( ['xterm', '-title', title, '-display ' + display, '-e', command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if mySW.services.isHTTP():
            serverIP = mySW.services.getHTTPip()
        else:
            return

        title = '"Download in progress..."'
        command = 'env TERM=ansi wget -O /dev/null %s/smallfile' % (serverIP)
        self.xtermCommand(MNnode, title, command)

    def startFTPDownload(self, MNnode):
        if mySW.services.isVSFTP():
            serverIP = mySW.services.getVSFTPip()
        else:
            return

        title = '"FTP Client"'
#        command = 'env TERM=ansi python ftpclient.py -s %s -lip %s -p 21 -u mininet -pw mininet' % (serverIP, MNnode.IP())
        command = 'env TERM=ansi python ftpclient.py -s %s -lip %s -p 21 -u dom -pw 11111' % (serverIP, MNnode.IP())
            # -s server
            # -lip local ip   ps: localhost wäre sinnvoll, geht aber nicht.
            # -p port
            # -u user
            # -pw password
        self.xtermCommand(MNnode, title, command)

    def startDHCP(self, MNnode):
        title = '"Client DHCP"'
        command = 'env TERM=ansi dhclient -d -v -lf /var/lib/dhcp/dhclient.leases.mn %s-eth0' % MNnode.name
        self.xtermCommand(MNnode, title, command)

    def startVOIP(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'asterisk &') #, preexec_fn=os.setsid )
        print "pid asterisk:", pid

        mySW.services.setVOIP(MNnode)
        return pid

#    def startEkiga(self, MNnode):
#        pid = mySW.instanceMN.sendCmd(MNnode, 'ekiga &') #, preexec_fn=os.setsid )
#        print "pid Ekiga:", pid
#        return pid

    def startLinphone(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'linphone &') #, preexec_fn=os.setsid )
        print "pid Linphone:", pid
        return pid

    def startYate(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'yate-qt4 &') #, preexec_fn=os.setsid )
        print "pid yate-qt4:", pid
        return pid


    def applyChanges(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return
# server services
        if self.cbSHTTP.isChecked() and not mySW.services.isHTTP() and self.cbSHTTP.isEnabled():
            self.http = self.startSimpleHTTPserver(MNnode)
        if not self.cbSHTTP.isChecked() and mySW.services.isHTTP() and self.cbSHTTP.isEnabled():
        #   kill HTTP server
            pass

        if self.cbSFTP.isChecked() and not mySW.services.isVSFTP() and self.cbSFTP.isEnabled():
            self.vsftp = self.startVSFTP(MNnode)

        if self.cbSDHCP.isChecked() and not mySW.services.isDHCP() and self.cbSDHCP.isEnabled():
            self.dhcpd = self.startDHCPD(MNnode)

        if self.cbSVOIP.isChecked() and not mySW.services.isVOIP() and self.cbSVOIP.isEnabled():
            self.voip = self.startVOIP(MNnode)

# client operations
        if self.cbDownload.isChecked():
            self.startDownload(MNnode)
            self.cbDownload.setChecked(False)

        if self.cbCFTP.isChecked():
            self.startFTPDownload(MNnode)
            self.cbCFTP.setChecked(False)

        if self.cbCDHCP.isChecked():
            self.startDHCP(MNnode)
            self.cbCDHCP.setChecked(False)

#        if self.cbCVOIPekiga.isChecked():
#            self.startEkiga(MNnode)
#            self.cbCVOIPekiga.setChecked(False)

        if self.cbCVOIPlinphone.isChecked():
            self.startLinphone(MNnode)
            self.cbCVOIPlinphone.setChecked(False)

        if self.cbCVOIPyate.isChecked():
            self.startYate(MNnode)
            self.cbCVOIPyate.setChecked(False)


    def xtermCommand(self, MNnode, title, command):
        display, tunnel = tunnelX11( MNnode, None )
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        return MNnode.popen( ['xterm', '-title', title, '-display ' + display, '-e', command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    def getSelectedMNnode(self):
        selectedHost = self.listHost.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        MNhost =  mySW.shortcut.getMNname(selectedHostText)  #e.g. h1
        return mySW.instanceMN.getNode(MNhost)      #object of h1

    def pbXtermclicked(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return

        title = '"bash on %s"' % (MNnode)
        command = 'env TERM=ansi bash'
        self.xtermCommand(MNnode, title, command)

    def pbSDHCPclicked(self):
        pass

    def pbSWiresharkclicked(self):
        pass

    def pbCFTPclicked(self):
        pass

    def pbCWiresharkclicked(self):
        pass

    def currentHostChanged(self, current, previous):
        self.showHostValues()
#        print current.text()   #e.g. Host05

    def showHostValues(self):

        selectedHost = self.listHost.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        info( '\n****** selectedHost:', str(selectedHost), '\n')
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        info( '\n****** selectedHostText:', str(selectedHostText), '\n')

        MNhost = mySW.shortcut.getMNname(selectedHostText)  #e.g. h1
        info( '\n****** MNhost:', str(MNhost), '\n')
        MNnode = mySW.instanceMN.getNode(MNhost)
        info( '\n****** MNNode:', str(MNnode), '\n')

        IP = mySW.instanceMN.getIP(MNhost)
        self.leIP.setText(IP)
        MAC = mySW.instanceMN.getMAC(MNhost)
        self.leMAC.setText(MAC)

# wenn DHCP läuft nicht
        if not mySW.services.isDHCP():
            self.cbSDHCP.setEnabled(True)
            self.cbSDHCP.setChecked(False)
        elif selectedHostText == mySW.services.getDHCPguiHost():
# DHCP löuft UND auf diesem Host
            self.cbSDHCP.setEnabled(True)
            self.cbSDHCP.setChecked(True)
# DHCP löuft aber nicht diesem Host
        else:
            self.cbSDHCP.setEnabled(False)
            self.cbSDHCP.setChecked(False) # oder doch True, falls man ein graues Kreuz haben will


# wenn HTTP läuft nicht
        if not mySW.services.isHTTP():
            self.cbSHTTP.setEnabled(True)
            self.cbSHTTP.setChecked(False)
        elif selectedHostText == mySW.services.getHTTPguiHost():
# HTTP löuft UND auf diesem Host
            self.cbSHTTP.setEnabled(True)
            self.cbSHTTP.setChecked(True)
# HTTP löuft aber nicht diesem Host
        else:
            self.cbSHTTP.setEnabled(False)
            self.cbSHTTP.setChecked(False) # oder doch True, falls man ein graues Kreuz haben will


# wenn FTP läuft nicht
        if not mySW.services.isVSFTP():
            self.cbSFTP.setEnabled(True)
            self.cbSFTP.setChecked(False)
        elif selectedHostText == mySW.services.getVSFTPguiHost():
# FTP löuft UND auf diesem Host
            self.cbSFTP.setEnabled(True)
            self.cbSFTP.setChecked(True)
# FTP löuft aber nicht diesem Host
        else:
            self.cbSFTP.setEnabled(False)
            self.cbSFTP.setChecked(False) # oder doch True, falls man ein graues Kreuz haben will


# wenn VOIP läuft nicht
        if not mySW.services.isVOIP():
            self.cbSVOIP.setEnabled(True)
            self.cbSVOIP.setChecked(False)
        elif selectedHostText == mySW.services.getVOIPguiHost():
# VOIP löuft UND auf diesem Host
            self.cbSVOIP.setEnabled(True)
            self.cbSVOIP.setChecked(True)
# VOIP löuft aber nicht diesem Host
        else:
            self.cbSVOIP.setEnabled(False)
            self.cbSVOIP.setChecked(False) # oder doch True, falls man ein graues Kreuz haben will

        self.cbDownload.setChecked(False)
        self.cbCFTP.setChecked(False)
        self.cbCDHCP.setChecked(False)
#        self.cbCVOIPekiga.setChecked(False)
        self.cbCVOIPlinphone.setChecked(False)
        self.cbCVOIPyate.setChecked(False)

# Tab Links:
## Connected to
#        connectionList = mySW.shortcut.getConnectedTo(selectedHostText)
#        print str(connectionList[0])
#        self.leConnectedTo.setText(str(connectionList[0]) + ", " +  #Switch01
#                                    str(mySW.shortcut.getMNname(connectionList[0])))   # s1
## Link delay (kann nicht aus MiniNet gelesen werden)
#        srcNode = mySW.instanceMN.getNode(MNhost)
#        destNode = mySW.shortcut.getMNname(connectionList[0])
#        destNode = mySW.instanceMN.getNode(destNode)
#
#        mySW.instanceMN.h1s1
#
#
#
#        links = srcNode.connectionsTo(destNode)
#        print links
#        srcLink = links[0][0]   # e.g.  h3-eth0
#        dstLink = links[0][1]   # e.g.  s1-eth3
#
#        srcLink.config(**{ 'bw' : 1, 'delay' : '1ms' })
#        dstLink.config(**{ 'bw' : 1, 'delay' : '1ms' })

#        params = mySW.instanceMN.net.linkInfo( srcNode, destNode )
#        print 'Link Parameters='+str(params)

## Paket loss

## Quere length


# Tab: Server services

# Tab: Client   --- nothing to check here ---




class RouterConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RouterConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confRouter.ui', self)
#        print "confRouter init...)"

        self.listRouter.currentItemChanged.connect(self.currentRouterChanged)


        for router in mySW.getNodeList("Router"):
            self.listRouter.addItem(router.objectName())


        HEADERS = ( "Link to", "Delay in ms",  "Delay in ms", "Paket loss", "Paket loss", 'Debug: print all' )
#treeWidget = treeInterfaces
        self.treeInterfaces.setColumnCount( len(HEADERS) )
        self.treeInterfaces.setHeaderLabels( HEADERS )

        # ----------------
        # Add Custom QTreeWidgetItem
        # ----------------
        ## Add Items:
        for name in [ 'host1', 'host2', 'host3', 'router1', 'router2', 'router4' ]:
            item = CustomTreeItem( self.treeInterfaces, name )

         ## Set Columns Width to match content:
        for column in range( self.treeInterfaces.columnCount() ):
            self.treeInterfaces.resizeColumnToContents( column )


        self.ptRoute.setPlainText(mySW.instanceMN.net[ 'r1' ].cmd( 'route' ))
#        print net[ 'r0' ].cmd( 'route' )


    def currentRouterChanged(self, current, previous):
        self.showRouterValues()

    def showRouterValues(self):

        selectedRouter = self.listRouter.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        info( '\n****** selectedRouter:', str(selectedRouter), '\n')
        if selectedRouter != None:
            selectedRouterText = selectedRouter.text()   #e.g. Host03

        info( '\n****** selectedRouterText:', str(selectedRouterText), '\n')

        MNrouter = mySW.shortcut.getMNname(selectedRouterText)  #e.g. h1
        info( '\n****** MNrouter:', str(MNrouter), '\n')
        MNnode = mySW.instanceMN.getNode(MNrouter)
        info( '\n****** MNRouter:', str(MNnode), '\n')

#        IP = mySW.instanceMN.getIP(MNrotuer)
#        self.leIP.setText(IP)
#        MAC = mySW.instanceMN.getMAC(MNrouter)
#        self.leMAC.setText(MAC)

        self.ptRoute.setPlainText(mySW.instanceMN.net[str(MNrouter)].cmd( 'route' ))


class LinkConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LinkConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confLink.ui', self)
#        print "linkconfig init...)"

        for link in mySW.getNodeList("Link"):
            self.listLink.addItem(link.objectName())

        self.listLink.currentItemChanged.connect(self.currentLinkChanged)

        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetButton)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.applyButton)
        self.hsDelay.valueChanged.connect(self.hsDelayChanged)
        self.sbDelay.valueChanged.connect(self.sbDelayChanged)
        self.hsLoss.valueChanged.connect(self.hsLossChanged)
        self.sbLoss.valueChanged.connect(self.sbLossChanged)
        self.hsQueue.valueChanged.connect(self.hsQueueChanged)
        self.sbQueue.valueChanged.connect(self.sbQueueChanged)


    def hsDelayChanged(self):
        self.sbDelay.setValue(self.hsDelay.value())

    def sbDelayChanged(self):
        self.hsDelay.setValue(self.sbDelay.value())

    def hsLossChanged(self):
        self.sbLoss.setValue(self.hsLoss.value())

    def sbLossChanged(self):
        self.hsLoss.setValue(self.sbLoss.value())

    def hsQueueChanged(self):
        self.sbQueue.setValue(self.hsQueue.value())

    def sbQueueChanged(self):
        self.hsQueue.setValue(self.sbQueue.value())

    def applyButton(self):
#        print "apply button link"
        self.applyChanges()

    def resetButton(self):
 #       print "reset buttton link"
        pass

    def accept(self):
#        print "accept/OK button link"
        self.applyChanges()
        QDialog.accept(self)

    def applyChanges(self):
        if self.selectedLink == None or \
           self.LinkNodes == None:
            print "linkconfig out1"
            return

        if self.delay == self.sbDelay.value() and \
           self.loss == self.sbLoss.value() and \
           self.swin == self.sbQueue.value():
            print "linkconfig out2"
            return   #nothing changed

# Link between this and that
        srcNode = mySW.instanceMN.getNode(self.source)
        destNode = mySW.instanceMN.getNode(self.destination)

        links = srcNode.connectionsTo(destNode)
#        print links
        srcLink = links[0][0]   # e.g.  h3-eth0
        dstLink = links[0][1]   # e.g.  s1-eth3
        srcLink.config(**{ 'delay' : str(self.sbDelay.value()) + 'ms', 'loss':self.sbLoss.value(), 'max_queue_size':self.sbQueue.value() })
        dstLink.config(**{ 'delay' : str(self.sbDelay.value()) + 'ms', 'loss':self.sbLoss.value(), 'max_queue_size':self.sbQueue.value() })

#        self.h1s1 = {'delay':str(self.defaultDelay) + 'ms','loss':0,'max_queue_size':None}

# save new value in parameter Class, too
        self.LinkNodes[2] = self.sbDelay.value()
        self.LinkNodes[3] = self.sbLoss.value()
        self.LinkNodes[4] = self.sbQueue.value()
        mySW.shortcut.setGUIlink(self.selectedLinkText, self.LinkNodes)


    def currentLinkChanged(self, current, previous):
        self.showLinkValues()
#        print current.text()   #e.g. Host05

    def showLinkValues(self):
# Link-Werte (delay, loss, ...)  können nicht aus MiniNet gelesen werden
# man müsste die tc Programme händisch auswerten.
# Deswegen werde die Soll-Werte aus der Parameter-Klasse geholt und
# bei Bedarf an Mininet übertragen. Die GUI Anzeige basiert auf den Soll-Werten

        self.selectedLink = self.listLink.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if self.selectedLink != None:
            self.selectedLinkText = self.selectedLink.text()   #e.g. Link01
        else:
            return

        self.LinkNodes = mySW.shortcut.getLinkSrcDest(self.selectedLinkText)  #e.g. h1
        if self.LinkNodes != None:
            self.source = self.LinkNodes[0]
            self.destination = self.LinkNodes[1]
            self.delay = self.LinkNodes[2]
            self.loss = self.LinkNodes[3]
            self.swin = self.LinkNodes[4]
            if self.swin == None:
                self.swin = 99
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(True)
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(True)
        else:
            self.source = ""
            self.destination = ""
            self.delay = 0
            self.loss = 0
            self.swin = 1
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)

        self.leSource.setText(self.source)
        self.leDestination.setText(self.destination)
        self.hsDelay.setValue(self.delay)
        self.sbDelay.setValue(self.delay)
        self.hsLoss.setValue(self.loss)
        self.sbLoss.setValue(self.loss)
        self.hsQueue.setValue(self.swin)
        self.sbQueue.setValue(self.swin)


class SwitchConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SwitchConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confSwitch.ui', self)
#        print "linkSwitch init...)"

        for host in mySW.getNodeList("Switch"):
            self.listSwitch.addItem(host.objectName())

        self.pbXterm.clicked.connect(self.pbXtermclicked)

    def pbXtermclicked(self):
        selectedHost = self.listSwitch.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        MNhost =  mySW.shortcut.getMNname(selectedHostText)  #e.g. h1
        tmpMNhost = mySW.instanceMN.getNode(MNhost)      #object of h1

        display, tunnel = tunnelX11( tmpMNhost, None )
        Title = '"bash on %s"' % (MNhost)
        self.p1 = tmpMNhost.popen( ['xterm', '-title', Title , '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)


# ------------------------------------------------------------------------------
# Custom QTreeWidgetItem
# ------------------------------------------------------------------------------
class CustomTreeItem( QtGui.QTreeWidgetItem ):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__( self, parent, name ):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''

        ## Init super class ( QtGui.QTreeWidgetItem )
        super( CustomTreeItem, self ).__init__( parent )

        ## Column 0 - Text:
        self.setText( 0, name )

        ## Column 1 - Slider:
        self.delay1 = QtGui.QSlider( orientation = Qt.Horizontal)
        self.delay1.setValue( 0 )
        self.treeWidget().setItemWidget( self, 1, self.delay1 )

        ## Column 2 - SpinBox:
        self.delay2 = QtGui.QSpinBox()
        self.delay2.setValue( 0 )
        self.treeWidget().setItemWidget( self, 2, self.delay2 )

        ## Column 3 - Slider:
        self.loss1 = QtGui.QSlider( orientation = Qt.Horizontal)
        self.loss1.setValue( 0 )
        self.treeWidget().setItemWidget( self, 3, self.loss1 )

        ## Column 4 - SpinBox:
        self.loss2 = QtGui.QSpinBox()
        self.loss2.setValue( 0 )
        self.treeWidget().setItemWidget( self, 4, self.loss2 )

        ## Column 5 - Button:
        self.button = QtGui.QPushButton()
        self.button.setText( "button %s" %name )
        self.treeWidget().setItemWidget( self, 5, self.button )

        ## Signals
        self.treeWidget().connect( self.button, QtCore.SIGNAL("clicked()"), self.buttonPressed )

    @property
    def name(self):
        '''
        Return name ( 1st column text )
        '''
        return self.text(0)

    @property
    def value(self):
        '''
        Return value ( 2nd column int)
        '''
        return self.delay1.value()

    def buttonPressed(self):
        '''
        Triggered when Item's button pressed.
        an example of using the Item's own values.
        '''
        print "This Item name:%s value:%i" %( self.name,
                                              self.value )


class Parameter():
    def __init__(self):
        # Schaffe Verknüpfung zwischen den GUI-Elementen
        # und den Mininet-Elementen

        self.GUIhosts = {}
        self.GUIhosts["Host01"] = "h1"
        self.GUIhosts["Host02"] = "h2"
        self.GUIhosts["Host03"] = "h3"
        self.GUIhosts["Host04"] = "h4"
        self.GUIhosts["Host05"] = "h5"
        self.GUIhosts["Host06"] = "h6"

        self.GUIswitches = {}
        self.GUIswitches["Switch01"] = "s1"
        self.GUIswitches["Switch02"] = "s2"

        self.GUIrouter = {}
        self.GUIrouter["Router01"] = "r1"
        self.GUIrouter["Router02"] = "r2"
        self.GUIrouter["Router03"] = "r3"
        self.GUIrouter["Router04"] = "r4"

        self.GUIlinks = {}
        defaultDelay = 20
#        self.GUIlinks["Link01"] = [source, dest, defaultDelay, loss, max_queue_size]
        self.GUIlinks["Link01"] = ["h1", "s1", defaultDelay, 0, None]
        self.GUIlinks["Link02"] = ["h2", "s1", defaultDelay, 0, None]
        self.GUIlinks["Link03"] = ["h3", "s1", defaultDelay, 0, None]
#        self.GUIlinks["Link04"] = ("s1", "r1")

# Nicht unique, d.h. jede Verbindung taucht zweimal auf.
        self.connections = {}
        self.connections["Host01"] = ["Switch01"]
        self.connections["Host02"] = ["Switch01"]
        self.connections["Host03"] = ["Switch01"]
        self.connections["Host04"] = ["Router02"]
        self.connections["Host05"] = ["Switch02"]
        self.connections["Host06"] = ["Switch02"]

        self.connections["Switch01"] = ["Host01", "Host02", "Host03", "Router01"]
        self.connections["Switch02"] = ["Host05", "Host06", "Router03"]

        self.connections["Router01"] = ["Switch01", "Router02", "Router04"]
        self.connections["Router02"] = ["Router01", "Router03", "Router04", "Host04"]
        self.connections["Router03"] = ["Router02", "Router04", "Switch20"]
        self.connections["Router04"] = ["Router01", "Router02", "Router03"]

    def setGUIlink(self, GUIname, param):
        if GUIname in self.GUIlinks:
            self.GUIlinks[GUIname] = param
        else:
            return None

    def getMNname(self, GUIname):
        info( '\n****** GUIname:', str(GUIname), '\n')
        info( '\n****** GUIhost\n', str(self.GUIhosts))
        if GUIname in self.GUIhosts.keys():
            return self.GUIhosts[str(GUIname)]
        elif GUIname in self.GUIswitches.keys():
            return self.GUIswitches[str(GUIname)]
        elif GUIname in self.GUIrouter.keys():
            return self.GUIrouter[str(GUIname)]
        else:
            return None

    def getGUIname(self, MNnode):
        for GUIhost in self.GUIhosts:
            if self.GUIhosts[str(GUIhost)] == MNnode.name:
                return GUIhost
        print "Dieser MN node (%s) ist keinem GUI host zugeordnet" % MNnode
        return None

    def getLinkSrcDest(self, GUIname):
        if GUIname in self.GUIlinks:
            return self.GUIlinks[str(GUIname)]
        else:
            return None

    def getConnectedTo(self, GUIname):
        if GUIname in self.connections:
            return self.connections[str(GUIname)]
        else:
            return None


class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('topo.ui', self)


        self.shortcut = Parameter()
        info( '\n****** shortcut()', str(self.shortcut), '\n')
        self.services = Services()
        info( '\n****** services()', str(self.services), '\n')

#old style
#        self.connect(self.ui.Host01, QtCore.SIGNAL("clicked()"), self.Host01clicked)

#new style
        self.Host01.clicked.connect(self.Host01clicked)
        self.Host02.clicked.connect(self.Host02clicked)
        self.Host03.clicked.connect(self.Host03clicked)
        self.Host04.clicked.connect(self.Host04clicked)
        self.Host05.clicked.connect(self.Host05clicked)
        self.Host06.clicked.connect(self.Host06clicked)

        self.Router01.clicked.connect(self.Router01clicked)
        self.Router02.clicked.connect(self.Router02clicked)
        self.Router03.clicked.connect(self.Router03clicked)
        self.Router04.clicked.connect(self.Router04clicked)

        self.Switch01.clicked.connect(self.Switch01clicked)

        self.Link01.clicked.connect(self.Link01clicked)
        self.Link02.clicked.connect(self.Link02clicked)
        self.Link03.clicked.connect(self.Link03clicked)
        self.Link04.clicked.connect(self.Link04clicked)
        self.Link05.clicked.connect(self.Link05clicked)
        self.Link06.clicked.connect(self.Link06clicked)
        self.Link07.clicked.connect(self.Link07clicked)
        self.Link08.clicked.connect(self.Link08clicked)
        self.Link09.clicked.connect(self.Link09clicked)
        self.Link10.clicked.connect(self.Link10clicked)
        self.Link11.clicked.connect(self.Link11clicked)
        self.Link12.clicked.connect(self.Link12clicked)

        self.bpStartMN.clicked.connect(self.StartMNclicked)
        self.bpStopMN.clicked.connect(self.StopMNclicked)
        self.bpRestartMN.clicked.connect(self.RestartMNclicked)
        self.pbCLI.clicked.connect(self.CLIclicked)

        self.pbExit.clicked.connect(self.pbExitclicked)

        self.debug1.clicked.connect(self.debug1clicked)
        self.debug2.clicked.connect(self.debug2clicked)
        self.debug3.clicked.connect(self.debug3clicked)
        self.debug4.clicked.connect(self.debug4clicked)
        self.debug5.clicked.connect(self.debug5clicked)

        self.updateProcesses()

#        self.drawLinks()

#    def drawLines(self, qp):
#
#        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
#
#        qp.setPen(pen)
#        qp.drawLine(20, 40, 250, 45)
#
##        pen.setStyle(QtCore.Qt.DashLine) #DashDotLine  DotLine DashDotDotLine CustomDashLine
##        qp.setPen(pen)
##        qp.drawLine(20, 80, 250, 85)


    def StartMNclicked(self):
        self.instanceMN = MN()
        self.instanceMN.startMN(MAC_random = self.cbRandomMAC.isChecked())

    def StopMNclicked(self):
        self.instanceMN.stopNet()

    def RestartMNclicked(self):
        self.StopMNclicked()
        self.StartMNclicked()

    def CLIclicked(self):
        mySW.instanceMN.startCLI()

    def debug1clicked(self):
        pass

    def debug2clicked(self):
        self.scen = MNtcp()
        self.scen.myNetwork( delay=20,
                          loss=3,
                          swin=3 )

    def debug3clicked(self):
        self.scen.startDownload( )

    def debug4clicked(self):
        self.scen.stopNet( )

    def debug5clicked(self):
        pass

    def debug6clicked(self):
        pass


    def getNodeList(self, Nodetype):
        """ extract all children of QWidget TopoArea for a
        certain type like Router, Host, Link, Switch
        Output: Host01, Host02, ... (as defined in Qt Designer) """
        anyList = []
        lineEdits = self.TopoArea.findChildren(QtGui.QWidget)
        Nodetypelen = len(Nodetype)
        for i in lineEdits:
            if i.objectName()[:Nodetypelen] == Nodetype:
                anyList.append(i)

        listSorted = sorted(anyList, key=lambda temp: temp.objectName())
#        for node in listSorted:
#            print node.objectName()

        return listSorted


    def updateProcesses(self):
        tree = self.runningServices  # replace every 'tree' with your QTreeWidget
        plist = []
        for host in self.getNodeList("Host"):
            plist.append(str(host.objectName()))

        clist=['Child 1','Child 2']
#        treeWidget=QtGui.QTreeWidget(self)
#        treeWidget.setGeometry(QtCore.QRect(50,50,150,140))
        tree.setHeaderLabels(["Host", "PID"])


        for parent in plist:
            pitems=QtGui.QTreeWidgetItem(tree)
            pitems.setText(0,parent)
            for child in clist:
                citems=QtGui.QTreeWidgetItem(pitems)
                citems.setText(0,child)


    def pbExitclicked(self):
        try:
            self.StopMNclicked()
        except:
            print "Mininet konnte nicht richtig beendet werden"
        exit(0)

    def drawLines(self, qp, fromx, fromy, tox, toy):

        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(fromx, fromy, tox, toy)


    def getCenter(self, widget):
#        print widget.geometry(), "left", widget.geometry().left(), "width", widget.geometry().width(), "top", widget.geometry().top(),  "height", widget.geometry().height()
        shiftx = self.TopoArea.geometry().left() + self.centralwidget.geometry().left()
        shifty = self.TopoArea.geometry().top() + self.centralwidget.geometry().top()
        centerx = shiftx + widget.geometry().left() + 0.5 * widget.geometry().width()
        centery = shifty + widget.geometry().top() + 0.5 * widget.geometry().height()

        return centerx, centery

    def drawMultiLinesObj(self, qp, source, *args):

        fromx, fromy = self.getCenter(source)
        for dest in args:
            tox, toy = self.getCenter(dest)
            self.drawLines(qp, fromx, fromy, tox, toy)


    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
# Left
        self.drawMultiLinesObj(qp, self.Switch01, self.Router01, self.Host01, self.Host02, self.Host03)
# Top
        self.drawMultiLinesObj(qp, self.Router02, self.Host04, self.Router01, self.Router02, self.Router03, self.Router04)
# Right
        self.drawMultiLinesObj(qp, self.Switch02, self.Router03, self.Host05, self.Host06)
# Bottom
        self.drawMultiLinesObj(qp, self.Router04, self.Router01, self.Router03)

        qp.end()

    def showHostWindow(self, Hostnumber) :
        myHost = HostConfig()
        info( '\n*** myhost erzeugt\n')
#        print ("hostconfig vor show")
        myHost.listHost.setCurrentRow(Hostnumber - 1)  #FIXME
        info( '\n****** host list auf erste,... gesetzt\n')
        myHost.showHostValues()
        myHost.exec_()
#        myHost.show()
#        QtGui.QMessageBox.information(self, "Hello", "Host 1 clicked!")

    def Host01clicked(self):
        self.showHostWindow(1)

    def Host02clicked(self):
        self.showHostWindow(2)

    def Host03clicked(self):
        self.showHostWindow(3)

    def Host04clicked(self):
        self.showHostWindow(4)

    def Host05clicked(self):
        self.showHostWindow(5)

    def Host06clicked(self):
        self.showHostWindow(6)


    def showRouterWindow(self, Routernumber) :
        myRouter = RouterConfig()
        print ("routerconfig vor show")
        myRouter.listRouter.setCurrentRow(Routernumber - 1)
        myRouter.exec_()

    def Router01clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showRouterWindow(1)

    def Router02clicked(self):
        self.showRouterWindow(2)

    def Router03clicked(self):
        self.showRouterWindow(3)

    def Router04clicked(self):
        self.showRouterWindow(4)


    def showSwitchWindow(self, Switchnumber) :
        mySwitch = SwitchConfig()
#        print ("switchconfig vor show")
        mySwitch.listSwitch.setCurrentRow(Switchnumber - 1)
        mySwitch.exec_()

    def Switch01clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showSwitchWindow(1)


    def showLinkWindow(self, Linknumber) :
        myLink = LinkConfig()
#        print ("linkconfig vor show")
        myLink.listLink.setCurrentRow(Linknumber - 1)
        myLink.exec_()

    def Link01clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showLinkWindow(1)

    def Link02clicked(self):
        self.showLinkWindow(2)

    def Link03clicked(self):
        self.showLinkWindow(3)

    def Link04clicked(self):
        self.showLinkWindow(4)

    def Link05clicked(self):
        self.showLinkWindow(5)

    def Link06clicked(self):
        self.showLinkWindow(6)

    def Link07clicked(self):
        self.showLinkWindow(7)

    def Link08clicked(self):
        self.showLinkWindow(8)

    def Link09clicked(self):
        self.showLinkWindow(9)

    def Link10clicked(self):
        self.showLinkWindow(10)

    def Link11clicked(self):
        self.showLinkWindow(11)

    def Link12clicked(self):
        self.showLinkWindow(12)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
 #   setLogLevel( 'info' )
    mySW = ControlMainWindow()
    mySW.StartMNclicked()
#    myNode = NodeConfig()
    mySW.show()
#    myNode.show()
    sys.exit(app.exec_())
