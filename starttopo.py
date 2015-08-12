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

defaultDelay = 5   #5ms default delay at each link (=minimal RTT is 10ms)

class MN():
    def startMN(self, MAC_random=True):
        self.createNet(MAC_random)
        self.createSwitch()
        self.createRouters()
        self.createHosts()
        self.createLinks()
        self.createRoutes()
        self.buildNet()
        self.startController()
        self.startSwitch()
        mySW.bpStartMN_enabled(False)
        mySW.bpStopMN_enabled(True)

    def getIP(self, host):
        tmphost = self.getNode(host)   #e.g. host = h1
        try:
            return tmphost.IP()
        except:
            print "kein entsprechenden MN Host-IP gefunden"
            return None
        return None

    def getMAC(self, host):
        tmphost = self.getNode(host)   #e.g. host = h1
        try:
            return tmphost.MAC()
        except:
            print "kein entsprechenden MN Host-MAC gefunden"
            return None
        return None

    def getNode(self, host):
        info('*** host type\n' + str(type(host)) + '\n')
        info('*** host details\n' + str(host) + '\n')

        try:
            return self.net.getNodeByName(host)   #e.g. host = h1
        except:
            print "Node %s existiert nicht" % host
            return None


    def createNet(self, MAC_random=True):
        if MAC_random == True:
            self.net = Mininet(topo=None,
                               build=False,
                               ipBase='10.0.0.0/8')
        else:
            self.net = Mininet(topo=None,
                               build=False,
                               autoSetMacs=True,
                               ipBase='10.0.0.0/8')

    def createSwitch(self):
        info('*** Add switches\n')
        self.s1 = self.net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
        self.s2 = self.net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')

    def createRouters(self):
        self.r1 = self.net.addHost(mySW.parameter.GUIrouter['Router01'], cls=Host, ip='10.0.0.100/24')
        self.r2 = self.net.addHost(mySW.parameter.GUIrouter['Router02'], cls=Host, ip='10.0.1.22/29')
        self.r3 = self.net.addHost(mySW.parameter.GUIrouter['Router03'], cls=Node, ip='10.0.1.33/29')
        self.r4 = self.net.addHost(mySW.parameter.GUIrouter['Router04'], cls=Node, ip='10.0.1.42/29')
        self.r1.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r2.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r3.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.r4.cmd('sysctl -w net.ipv4.ip_forward=1')

    def createHosts(self):
        self.h1 = self.net.addHost(mySW.parameter.GUIhosts['Host01'], cls=Host, ip='10.0.0.1/24', defaultRoute='via 10.0.0.100')
        self.h2 = self.net.addHost(mySW.parameter.GUIhosts['Host02'], cls=Host, ip='10.0.0.2/24', defaultRoute='via 10.0.0.100')
        self.h3 = self.net.addHost(mySW.parameter.GUIhosts['Host03'], cls=Host, ip='10.0.0.3/24', defaultRoute='via 10.0.0.100')
        self.h4 = self.net.addHost(mySW.parameter.GUIhosts['Host04'], cls=Host, ip='10.0.1.17/29', defaultRoute='via 10.0.1.22')
        self.h5 = self.net.addHost(mySW.parameter.GUIhosts['Host05'], cls=Host, ip='10.0.1.34/29', defaultRoute='via 10.0.1.33')
        self.h6 = self.net.addHost(mySW.parameter.GUIhosts['Host06'], cls=Host, ip='10.0.1.35/29', defaultRoute='via 10.0.1.33')

    def createLinks(self):
#        defaultDelay = 5
        default_link = {'delay':str(defaultDelay) + 'ms', 'loss':0, 'max_queue_size':None}
# Sub-net A: 10.0.0.0/24
        self.net.addLink(self.h1, self.s1, cls=TCLink, **default_link)
        self.net.addLink(self.h2, self.s1, cls=TCLink, **default_link)
        self.net.addLink(self.h3, self.s1, cls=TCLink, **default_link)
        self.net.addLink(self.s1, self.r1, cls=TCLink, **default_link)
        self.r1.setIP('10.0.0.100', prefixLen=24, intf='r1-eth0')

# Sub-net C: 10.0.1.16/29
        self.net.addLink(self.h4, self.r2, cls=TCLink, **default_link)

# Sub-net E: 10.0.1.32/29
        self.net.addLink(self.h5, self.s2, cls=TCLink, **default_link)
        self.net.addLink(self.h6, self.s2, cls=TCLink, **default_link)
        self.net.addLink(self.s2, self.r3, cls=TCLink, **default_link)

# Sub-net B: 10.0.1.8/29
        self.net.addLink(self.r1, self.r2, cls=TCLink, **default_link)
        self.r1.setIP('10.0.1.9', prefixLen=29, intf='r1-eth1')
        self.r2.setIP('10.0.1.10', prefixLen=29, intf='r2-eth1')

# Sub-net D: 10.0.1.24/29
        tmplink = self.net.addLink(self.r2, self.r3, cls=TCLink, **default_link)
        self.r2.setIP('10.0.1.25', prefixLen=29, intf='r2-eth2')
        tmplink.intf2.setIP('10.0.1.26/29') #entspricht r3-eth1

# Sub-net F: 10.0.1.40/29
        tmplink = self.net.addLink(self.r3, self.r4, cls=TCLink, **default_link)
        self.r3.setIP('10.0.1.41', prefixLen=29, intf='r3-eth2')
        tmplink.intf2.setIP('10.0.1.42/29') #entspricht r4-eth0 

# Sub-net G: 10.0.1.48/29
        tmplink = self.net.addLink(self.r1, self.r4, cls=TCLink, **default_link)
        self.r1.setIP('10.0.1.50', prefixLen=29, intf='r1-eth2')
        tmplink.intf2.setIP('10.0.1.49/29') #entspricht r4-eth1

# Sub-net H: 10.0.1.56/29
        tmplink = self.net.addLink(self.r2, self.r4, cls=TCLink, **default_link)
        self.r2.setIP('10.0.1.57', prefixLen=29, intf='r2-eth3')
        tmplink.intf2.setIP('10.0.1.58/29') #entspricht r4-eth2

    def modifyLink(self, link, param):
        pass

    def createRoutes(self):

        self.r1.cmd('ip route add 10.0.1.16/29 via 10.0.1.10') #Sub-net C
        self.r1.cmd('ip route add 10.0.1.24/29 via 10.0.1.10') #Sub-net D
        self.r1.cmd('ip route add 10.0.1.32/29 via 10.0.1.10') #Sub-net E
        self.r1.cmd('ip route add 10.0.1.40/29 via 10.0.1.49') #Sub-net F
        self.r1.cmd('ip route add 10.0.1.56/29 via 10.0.1.49') #Sub-net H

        self.r2.cmd('ip route add 10.0.0.0/24 via 10.0.1.9') #Sub-net A
        self.r2.cmd('ip route add 10.0.1.32/29 via 10.0.1.26') #Sub-net E
        self.r2.cmd('ip route add 10.0.1.40/29 via 10.0.1.58') #Sub-net F
        self.r2.cmd('ip route add 10.0.1.48/29 via 10.0.1.58') #Sub-net G

        self.r3.cmd('ip route add 10.0.1.16/29 via 10.0.1.25') #Sub-net C
        self.r3.cmd('ip route add 10.0.1.56/29 via 10.0.1.42') #Sub-net H
        self.r3.cmd('ip route add 10.0.1.8/29 via 10.0.1.25') #Sub-net B
        self.r3.cmd('ip route add 10.0.1.48/29 via 10.0.1.42') #Sub-net G
        self.r3.cmd('ip route add 10.0.0.0/24 via 10.0.1.25') #Sub-net A

        self.r4.cmd('ip route add 10.0.0.0/24 via 10.0.1.50') #Sub-net A
        self.r4.cmd('ip route add 10.0.1.8/29 via 10.0.1.50') #Sub-net B
        self.r4.cmd('ip route add 10.0.1.16/29 via 10.0.1.57') #Sub-net C
        self.r4.cmd('ip route add 10.0.1.24/29 via 10.0.1.41') #Sub-net D
        self.r4.cmd('ip route add 10.0.1.32/29 via 10.0.1.41') #Sub-net E

    def buildNet(self):
        self.net.build()

    def startController(self):
        info('*** Starting controllers\n')
        for self.controller in self.net.controllers:
            self.controller.start()

    def startSwitch(self):
        info('*** Starting switches\n')
        self.net.get('s1').start([])
        self.net.get('s2').start([])

    def startCLI(self):
        CLI( self.net )

    def stopNet( self ):
        subprocess.Popen(["pkill", "dhcpd"])
        subprocess.Popen(["pkill", "asterisk"])
        subprocess.Popen(["pkill", "vsftp"])

        try:
            self.net.stop()
        except:
#            print "probleme1"
            pass

        mySW.bpStartMN_enabled(True)
        mySW.bpStopMN_enabled(False)

    def sendCmd( self, node, command ):
        return node.cmd(command, shell=True, printPid=True)


class Services():
    def __init__(self):
        self.DHCPnode = None
        self.HTTPnode = None
        self.VSFTPnode = None
        self.VOIPnode = None
        self.fresh_daemon_leases = True
        self.fresh_client_leases = True

#        print "Klasse Services aufgerufen"

    def setDHCP(self, MNnode):
        self.DHCPnode = MNnode
        print "DHCPnode gesetzt:", self.DHCPnode

    def getDHCPip(self):
        if self.DHCPnode != None:
            return self.DHCPnode.IP()

    def getDHCPguiHost(self):
        if self.DHCPnode != None:
            return mySW.parameter.getGUIname(self.DHCPnode)

    def isDHCP(self):
#        print "isDHCP", self.DHCPnode
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
            return mySW.parameter.getGUIname(self.VSFTPnode)

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
            return mySW.parameter.getGUIname(self.VOIPnode)

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
            return mySW.parameter.getGUIname(self.HTTPnode)

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
#        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetButton)
        self.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.applyButton)

        self.listHost.currentItemChanged.connect(self.currentHostChanged)
        self.pbXterm.clicked.connect(self.pbXtermclicked)
#Server tab
        self.pbSDHCP.clicked.connect(self.pbSDHCPclicked)
        self.pbSWireshark.clicked.connect(self.pbSWiresharkclicked)
        self.pbSDHCP.clicked.connect(self.showDHCPWindow)
#Client tab
#        self.pbCFTP.clicked.connect(self.pbCFTPclicked)
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
        self.currentObj.setStyleSheet("")
        QDialog.accept(self)
#        self.close()

    def reject(self):
        self.currentObj.setStyleSheet("")
        QDialog.reject(self)

    def startSimpleHTTPserver(self, MNnode):
        info('\n****** execute startHTTPserver on %s\n' % MNnode.name) #selectedHostText)
        pid = mySW.instanceMN.sendCmd(MNnode, "python -m SimpleHTTPServer 80 &")
        print "pid http:", pid

        mySW.services.setHTTP(MNnode)

        return pid

    def startVSFTP(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'vsftpd &') #, preexec_fn=os.setsid )
        print "pid vsftpd:", pid

        mySW.services.setVSFTP(MNnode)
        return pid

    def startDHCPD(self, MNnode):   #, fresh_daemon_leases = True):
        info('\n****** execute DHCP server on %s\n' % MNnode.name)
        print "copy configuration file to /etc/dhcp/dhcpd_mn.conf"
        MNnode.cmd("cp ./dhcpd_mn.conf /etc/dhcp/", printPid=True)
        if mySW.services.fresh_daemon_leases:
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
            mySW.changeStatus("Error: No HTTP server started")            
            return

        title = '"Download in progress..."'
        command = 'env TERM=ansi wget -O /dev/null %s/smallfile' % (serverIP)
        self.xtermCommand(MNnode, title, command)
        mySW.changeStatus("Download started from a HTTP server")


    def startWWW(self, MNnode):
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
#            self.p1 = MNnode.popen( ['xterm', '-title', title, '-display ' + display, '-e', command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        if mySW.services.isHTTP():
            serverIP = mySW.services.getHTTPip()
        else:
            mySW.changeStatus("Error: No HTTP server started")
            return

        command = 'firefox %s &' % (serverIP)

        pid = mySW.instanceMN.sendCmd(MNnode, command)  #, preexec_fn=os.setsid )
        print "pid firefox:", pid
        mySW.changeStatus("View web site in Firefox")
        return pid


    def startFTPDownload(self, MNnode):
        if mySW.services.isVSFTP():
            serverIP = mySW.services.getVSFTPip()
        else:
            mySW.changeStatus("Error: No FTP server started")
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
        mySW.changeStatus("FTP Download started")


    def startDHCP(self, MNnode):
#        if fresh_client_leases == True:
#            print "delete /var/lib/dhcp/dhclient.leases.mn"
#            self.h2.cmd("rm /var/lib/dhcp/dhclient.leases.mn", printPid=True)
#            self.h2.cmd("touch /var/lib/dhcp/dhclient.leases.mn", printPid=True)
#        else:
#            print "verwende vorhandene /var/lib/dhcp/dhclient.leases.mn"
#            self.h2.cmd("touch /var/lib/dhcp/dhclient.leases.mn", printPid=True)


        title = '"Client DHCP"'
        command = 'env TERM=ansi dhclient -d -v -lf /var/lib/dhcp/dhclient.leases.mn %s-eth0' % MNnode.name
        self.xtermCommand(MNnode, title, command)
        mySW.changeStatus("DHCP client started")

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
        mySW.changeStatus("VoIP softphone \"Linphone\" started")
        return pid

    def startYate(self, MNnode):
        pid = mySW.instanceMN.sendCmd(MNnode, 'yate-qt4 &') #, preexec_fn=os.setsid )
        print "pid yate-qt4:", pid
        mySW.changeStatus("VoIP softphone \"Yate\" started")
        return pid


    def applyChanges(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return
# server services
# HTTP
        if self.cbSHTTP.isChecked() and not mySW.services.isHTTP() and self.cbSHTTP.isEnabled():
            self.http = self.startSimpleHTTPserver(MNnode)
            mySW.changeStatus("A simple HTTP server has been started")
        if not self.cbSHTTP.isChecked() and mySW.services.isHTTP() and self.cbSHTTP.isEnabled():
            print "kill HTTP server...", self.http
            MNnode.cmd("sudo pkill -f \"python -m SimpleHTTPServer 80\"")
            mySW.services.setHTTP(None)
            mySW.changeStatus("The simple HTTP server has been stopped")

# FTP
        if self.cbSFTP.isChecked() and not mySW.services.isVSFTP() and self.cbSFTP.isEnabled():
            self.vsftp = self.startVSFTP(MNnode)
            mySW.changeStatus("A FTP server (vsftp) has been started")
        if not self.cbSFTP.isChecked() and mySW.services.isVSFTP() and self.cbSFTP.isEnabled():
#            print "kill FTP server...", self.vsftp
            MNnode.cmd("pkill vsftp")
            mySW.services.setVSFTP(None)
            mySW.changeStatus("The FTP server (vsftp) has been stopped")

# DHCP
        if self.cbSDHCP.isChecked() and not mySW.services.isDHCP() and self.cbSDHCP.isEnabled():
            self.dhcpd = self.startDHCPD(MNnode)
            mySW.changeStatus("A DHCP server (dhcpd) has been started")
        if not self.cbSDHCP.isChecked() and mySW.services.isDHCP() and self.cbSDHCP.isEnabled():
#            print "kill DHCP server...", self.dhcpd
            MNnode.cmd("pkill dhcpd")
            mySW.services.setDHCP(None)
            mySW.changeStatus("The DHCP server (dhcpd) has been stopped")

# VoIP
        if self.cbSVOIP.isChecked() and not mySW.services.isVOIP() and self.cbSVOIP.isEnabled():
            self.voip = self.startVOIP(MNnode)
            mySW.changeStatus("A VoIP server (asterisk) has been started")
        if not self.cbSVOIP.isChecked() and mySW.services.isVOIP() and self.cbSVOIP.isEnabled():
#            print "kill VoIP server...", self.voip
            MNnode.cmd("pkill asterisk")
            mySW.services.setVOIP(None)
            mySW.changeStatus("The VoIP server (asterisk) has been stopped")

# client operations
        if self.cbDownload.isChecked():
            self.startDownload(MNnode)
            self.cbDownload.setChecked(False)

        if self.cbWWW.isChecked():
            self.startWWW(MNnode)
            self.cbWWW.setChecked(False)

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
        display, tunnel = tunnelX11(MNnode, None)
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        return MNnode.popen(['xterm', '-title', title, '-display ' + display, '-e', command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)

    def getSelectedMNnode(self):
        selectedHost = self.listHost.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        MNhost = mySW.parameter.getMNname(selectedHostText)  #e.g. h1
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
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return

# server services
        counter = 0
        if self.cbSHTTP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y ip.addr==%s &' % (MNnode.name, MNnode.IP())
            counter += 1

        if self.cbSFTP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y "ftp || ftp-data" &' % (MNnode.name)   # %s = 'h1'
            counter += 1

        if self.cbSDHCP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y bootp.dhcp==1 &' % (MNnode.name)
            counter += 1

        if self.cbSVOIP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y "sip || rtp" &' % (MNnode.name)
            counter += 1

        if counter == 0 or counter >= 2: # don't use any special display filter
            wsCommand = 'wireshark -i %s-eth0 -k &' % (MNnode.name)

        display, tunnel = tunnelX11(MNnode, None)
        self.sws = MNnode.cmd([wsCommand], shell=True, printPid=True)
        print "pid wireshark: ", self.sws


    def pbCFTPclicked(self):
        pass

    def pbCWiresharkclicked(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return

# client operations
        counter = 0
        if self.cbDownload.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y ip.addr==%s &' % (MNnode.name, MNnode.IP())
            counter += 1

        if self.cbCFTP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y "ftp || ftp-data" &' % (MNnode.name)   # %s = 'h1'
            counter += 1

        if self.cbCDHCP.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y bootp.dhcp==1 &' % (MNnode.name)
            counter += 1

        if self.cbCVOIPlinphone.isChecked() or self.cbCVOIPyate.isChecked():
            wsCommand = 'wireshark -i %s-eth0 -k -Y "sip || rtp" &' % (MNnode.name)
            counter += 1

        if counter == 0 or counter >= 2: # don't use any special display filter
            wsCommand = 'wireshark -i %s-eth0 -k &' % (MNnode.name)

        display, tunnel = tunnelX11(MNnode, None)
        self.cws = MNnode.cmd( [wsCommand], shell=True, printPid=True)
        print "pid wireshark: ", self.cws


    def currentHostChanged(self, current, previous):
        self.showHostValues()
#        print current.text()   #e.g. Host05
        self.currentObj = mySW.TopoArea.findChild(QtGui.QWidget, current.text())
        self.currentObj.setStyleSheet("background-color: rgb(0, 170, 255);")

        if previous != None:
            previousObj = mySW.TopoArea.findChild(QtGui.QWidget, previous.text())
            previousObj.setStyleSheet("")


    def showHostValues(self):

        selectedHost = self.listHost.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        info('\n****** selectedHost:', str(selectedHost), '\n')
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        info('\n****** selectedHostText:', str(selectedHostText), '\n')

        MNhost = mySW.parameter.getMNname(selectedHostText)  #e.g. h1
        info('\n****** MNhost:', str(MNhost), '\n')
        MNnode = mySW.instanceMN.getNode(MNhost)
        info('\n****** MNNode:', str(MNnode), '\n')

        IP = mySW.instanceMN.getIP(MNhost)
        self.leIP.setText(IP)
        MAC = mySW.instanceMN.getMAC(MNhost)
        self.leMAC.setText(MAC)
        self.leName.setText(MNhost)
        INTERFACES = MNnode.intfNames()
        self.leInferface.setText(str(INTERFACES[0]))



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
#        connectionList = mySW.parameter.getConnectedTo(selectedHostText)
#        print str(connectionList[0])
#        self.leConnectedTo.setText(str(connectionList[0]) + ", " +  #Switch01
#                                    str(mySW.parameter.getMNname(connectionList[0])))   # s1
## Link delay (kann nicht aus MiniNet gelesen werden)
#        srcNode = mySW.instanceMN.getNode(MNhost)
#        destNode = mySW.parameter.getMNname(connectionList[0])
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

    def showDHCPWindow(self, Hostnumber):
        myDHCP = DHCPConfig()
#        info( '\n*** myhost erzeugt\n')
#        print ("hostconfig vor show")
#        myHost.listHost.setCurrentRow(Hostnumber - 1)  #FIXME
#        info( '\n****** host list auf erste,... gesetzt\n')
        myDHCP.showDHCPValues()
        myDHCP.exec_()




class DHCPConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(DHCPConfig, self).__init__(parent)
        print "confDHCP loaded"
        uic.loadUi('confDHCP.ui', self)


    def accept(self):
#        print "accept/OK button"
        self.applyChanges()
        QDialog.accept(self)

    def applyChanges(self):
        mySW.services.fresh_daemon_leases = self.DHCP_daemon_leases.isChecked()
        mySW.services.fresh_client_leases = self.DHCP_client_leases.isChecked()

    def showDHCPValues(self):
        self.DHCP_daemon_leases.setChecked(mySW.services.fresh_daemon_leases)
        self.DHCP_client_leases.setChecked(mySW.services.fresh_client_leases)


class RouterConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RouterConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confRouter.ui', self)
#        print "confRouter init...)"

        self.listRouter.currentItemChanged.connect(self.currentRouterChanged)
        self.pbXterm.clicked.connect(self.pbXtermclicked)
        self.pbWireshark.clicked.connect(self.pbWiresharkclicked)



        for router in mySW.getNodeList("Router"):
            self.listRouter.addItem(router.objectName())


#        HEADERS = ("Link to", "Delay in ms", "Delay in ms", "Paket loss", "Paket loss", 'Debug: print all')
##treeWidget = treeInterfaces
#        self.treeInterfaces.setColumnCount(len(HEADERS))
#        self.treeInterfaces.setHeaderLabels(HEADERS)
#
#        # ----------------
#        # Add Custom QTreeWidgetItem
#        # ----------------
#        ## Add Items:
#        for name in ['host1', 'host2', 'host3', 'router1', 'router2', 'router4']:
#            item = CustomTreeItem( self.treeInterfaces, name )
#
#         ## Set Columns Width to match content:
#        for column in range( self.treeInterfaces.columnCount()):
#            self.treeInterfaces.resizeColumnToContents(column)
#
#
##        self.ptRoute.setPlainText(mySW.instanceMN.net['r1'].cmd('route'))
##        print net[ 'r0' ].cmd( 'route' )

    def pbXtermclicked(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return

        title = '"bash on %s"' % (MNnode)
        command = 'env TERM=ansi bash'
        self.xtermCommand(MNnode, title, command)

    def xtermCommand(self, MNnode, title, command):
        display, tunnel = tunnelX11(MNnode, None)
#        self.p1 = self.h4.popen( ['xterm', '-title', 'BlaBla', '-display ' + display, '-e', 'env TERM=ansi bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        return MNnode.popen(['xterm', '-title', title, '-display ' + display, '-e', command], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    
    def pbWiresharkclicked(self):
        MNnode = self.getSelectedMNnode()
        if MNnode == None:
            return

        wsCommand = 'wireshark &'
        display, tunnel = tunnelX11(MNnode, None)
        self.sws = MNnode.cmd([wsCommand], shell=True, printPid=True)
        print "pid wireshark: ", self.sws

    def getSelectedMNnode(self):
        selectedRouter = self.listRouter.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if selectedRouter != None:
            selectedRouterText = selectedRouter.text()   #e.g. Router01

        MNrouter = mySW.parameter.getMNname(selectedRouterText)  #e.g. r1
        return mySW.instanceMN.getNode(MNrouter)      #object of r1

    def accept(self):
#        print "accept/OK button"
#        self.applyChanges()
        self.currentObj.setStyleSheet("")
        QDialog.accept(self)
#        self.close()

    def reject(self):
        self.currentObj.setStyleSheet("")
        QDialog.reject(self)


    def currentRouterChanged(self, current, previous):
        self.showRouterValues()

        self.currentObj = mySW.TopoArea.findChild(QtGui.QWidget, current.text())
        self.currentObj.setStyleSheet("background-color: rgb(0, 170, 255);")

        if previous != None:
            previousObj = mySW.TopoArea.findChild(QtGui.QWidget, previous.text())
            previousObj.setStyleSheet("")


    def showRouterValues(self):

        selectedRouter = self.listRouter.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        info('\n****** selectedRouter:', str(selectedRouter), '\n')
        if selectedRouter != None:
            selectedRouterText = selectedRouter.text()   #e.g. Host03

        info('\n****** selectedRouterText:', str(selectedRouterText), '\n')

        MNrouter = mySW.parameter.getMNname(selectedRouterText)  #e.g. h1
        info('\n****** MNrouter:', str(MNrouter), '\n')
        MNnode = mySW.instanceMN.getNode(MNrouter)
        info('\n****** MNRouter:', str(MNnode), '\n')

#        IP = mySW.instanceMN.getIP(MNrotuer)
#        self.leIP.setText(IP)
#        MAC = mySW.instanceMN.getMAC(MNrouter)
#        self.leMAC.setText(MAC)

        self.ptRoute.setPlainText(mySW.instanceMN.net[str(MNrouter)].cmd('route'))
        self.ptLinks.setPlainText(mySW.instanceMN.net[str(MNrouter)].cmd('ip a'))


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

#        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(self.resetButton)
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

    def reject(self):
        self.currentObj.setStyleSheet("")
        QDialog.reject(self)

    def applyChanges(self):
        if self.selectedLink == None or \
           self.LinkNodes == None:
            print "No valid link selected"
            return

        if self.delay == self.sbDelay.value() and \
           self.loss == self.sbLoss.value() and \
           self.swin == self.sbQueue.value():
            mySW.changeStatus("No values were changed")
            return   #nothing changed

# Link between this and that
        srcNode = mySW.instanceMN.getNode(self.source)
        destNode = mySW.instanceMN.getNode(self.destination)

        links = srcNode.connectionsTo(destNode)
#        print links
        srcLink = links[0][0]   # e.g.  h3-eth0
        dstLink = links[0][1]   # e.g.  s1-eth3
        srcLink.config(**{'delay' : str(self.sbDelay.value()) + 'ms', \
                          'loss' : self.sbLoss.value(), \
                          'max_queue_size' : self.sbQueue.value()})
        dstLink.config(**{'delay' : str(self.sbDelay.value()) + 'ms', \
                          'loss' : self.sbLoss.value(), \
                          'max_queue_size' : self.sbQueue.value()})

#        self.h1s1 = {'delay':str(self.defaultDelay) + 'ms',
#                     'loss':0,
#                     'max_queue_size':None}

# save new value in parameter Class, too
        self.LinkNodes[2] = self.sbDelay.value()
        self.LinkNodes[3] = self.sbLoss.value()
        self.LinkNodes[4] = self.sbQueue.value()
        mySW.parameter.setGUIlink(self.selectedLinkText, self.LinkNodes)
        self.showLinkValues()
        mySW.changeStatus("Link values changed")


    def currentLinkChanged(self, current, previous):
        self.showLinkValues()
#        print current.text()   #e.g. Host05

        self.currentObj = mySW.TopoArea.findChild(QtGui.QWidget, current.text())
        self.currentObj.setStyleSheet("background-color: rgb(0, 170, 255);")

        if previous != None:
            previousObj = mySW.TopoArea.findChild(QtGui.QWidget, previous.text())
            previousObj.setStyleSheet("")

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

        self.LinkNodes = mySW.parameter.getLinkSrcDest(self.selectedLinkText)  #e.g. h1
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
#            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(True)
        else:
            self.source = ""
            self.destination = ""
            self.delay = 0
            self.loss = 0
            self.swin = 1
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
            self.buttonBox.button(QDialogButtonBox.Apply).setEnabled(False)
#            self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)

        scrObj = mySW.instanceMN.getNode(self.source)
        dstObj = mySW.instanceMN.getNode(self.destination)

        self.leSrcName.setText(mySW.parameter.getGUIname(scrObj) + ", " + self.source)
        self.leDstName.setText(mySW.parameter.getGUIname(dstObj) + ", " + self.destination)

        src = mySW.instanceMN.getNode(self.source)
        dst = mySW.instanceMN.getNode(self.destination)
        srcIntf = src.connectionsTo(dst)[0][0]
        dstIntf = src.connectionsTo(dst)[0][1]

        self.leSrcIP.setText(srcIntf.IP())
        self.leDstIP.setText(dstIntf.IP())

        self.leSrcIntf.setText(srcIntf.name)
        self.leDstIntf.setText(dstIntf.name)

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

        self.listSwitch.currentItemChanged.connect(self.currentSwitchChanged)

        self.pbXterm.clicked.connect(self.pbXtermclicked)

    def accept(self):
#        print "accept/OK button link"
#        self.applyChanges()
        QDialog.accept(self)

    def reject(self):
        self.currentObj.setStyleSheet("")
        QDialog.reject(self)


    def pbXtermclicked(self):
        selectedHost = self.listSwitch.currentItem()   #e.g <PyQt4.QtGui.QListWidgetItem object at 0x7f0ce01fa0e8>
        if selectedHost != None:
            selectedHostText = selectedHost.text()   #e.g. Host03

        MNhost = mySW.parameter.getMNname(selectedHostText)  #e.g. h1
        tmpMNhost = mySW.instanceMN.getNode(MNhost)      #object of h1

        display, tunnel = tunnelX11(tmpMNhost, None)
        Title = '"bash on %s"' % (MNhost)
        self.p1 = tmpMNhost.popen(['xterm', \
                                   '-title', Title, \
                                   '-display ' + display, \
                                   '-e', 'env TERM=ansi bash'], \
                                   stdin=subprocess.PIPE, \
                                   stdout=subprocess.PIPE, \
                                   shell=True)

    def currentSwitchChanged(self, current, previous):
#        self.showSwitchValues()
#        print current.text()   #e.g. Host05

        self.currentObj = mySW.TopoArea.findChild(QtGui.QWidget, current.text())
        self.currentObj.setStyleSheet("background-color: rgb(0, 170, 255);")

        if previous != None:
            previousObj = mySW.TopoArea.findChild(QtGui.QWidget, previous.text())
            previousObj.setStyleSheet("")


# ------------------------------------------------------------------------------
# Custom QTreeWidgetItem
# ------------------------------------------------------------------------------
class CustomTreeItem(QtGui.QTreeWidgetItem):
    '''
    Custom QTreeWidgetItem with Widgets
    '''

    def __init__(self, parent, name):
        '''
        parent (QTreeWidget) : Item's QTreeWidget parent.
        name   (str)         : Item's name. just an example.
        '''

        ## Init super class ( QtGui.QTreeWidgetItem )
        super(CustomTreeItem, self).__init__(parent)

        ## Column 0 - Text:
        self.setText(0, name)

        ## Column 1 - Slider:
        self.delay1 = QtGui.QSlider(orientation=Qt.Horizontal)
        self.delay1.setValue(0)
        self.treeWidget().setItemWidget(self, 1, self.delay1)

        ## Column 2 - SpinBox:
        self.delay2 = QtGui.QSpinBox()
        self.delay2.setValue(0)
        self.treeWidget().setItemWidget(self, 2, self.delay2)

        ## Column 3 - Slider:
        self.loss1 = QtGui.QSlider(orientation=Qt.Horizontal)
        self.loss1.setValue(0)
        self.treeWidget().setItemWidget(self, 3, self.loss1)

        ## Column 4 - SpinBox:
        self.loss2 = QtGui.QSpinBox()
        self.loss2.setValue(0)
        self.treeWidget().setItemWidget(self, 4, self.loss2)

        ## Column 5 - Button:
        self.button = QtGui.QPushButton()
        self.button.setText( "button %s" %name )
        self.treeWidget().setItemWidget(self, 5, self.button)

        ## Signals
        self.treeWidget().connect(self.button, QtCore.SIGNAL("clicked()"), self.buttonPressed)

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
        print "This Item name:%s value:%i" %(self.name,
                                             self.value)


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
#        defaultDelay = 5   #FIXME
#        self.GUIlinks["Link01"] = [source, dest, defaultDelay, loss, max_queue_size]
        self.GUIlinks["Link01"] = ["h1", "s1", defaultDelay, 0, None]
        self.GUIlinks["Link02"] = ["h2", "s1", defaultDelay, 0, None]
        self.GUIlinks["Link03"] = ["h3", "s1", defaultDelay, 0, None]
        self.GUIlinks["Link04"] = ["s1", "r1", defaultDelay, 0, None]

        self.GUIlinks["Link05"] = ["h4", "r2", defaultDelay, 0, None]
        self.GUIlinks["Link06"] = ["h5", "s2", defaultDelay, 0, None]
        self.GUIlinks["Link07"] = ["h6", "s2", defaultDelay, 0, None]
        self.GUIlinks["Link08"] = ["r1", "r2", defaultDelay, 0, None]
        self.GUIlinks["Link09"] = ["r2", "r3", defaultDelay, 0, None]
        self.GUIlinks["Link10"] = ["r1", "r4", defaultDelay, 0, None]
        self.GUIlinks["Link11"] = ["r2", "r3", defaultDelay, 0, None]
        self.GUIlinks["Link12"] = ["r2", "r4", defaultDelay, 0, None]
        self.GUIlinks["Link13"] = ["s2", "r3", defaultDelay, 0, None]


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
        info('\n****** GUIname:', str(GUIname), '\n')
        info('\n****** GUIhost\n', str(self.GUIhosts))
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

        for GUIswitch in self.GUIswitches:
            if self.GUIswitches[str(GUIswitch)] == MNnode.name:
                return GUIswitch

        for GUIroute in self.GUIrouter:
            if self.GUIrouter[str(GUIroute)] == MNnode.name:
                return GUIroute

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

    cli_do = pyqtSignal()

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('topo.ui', self)


        self.parameter = Parameter()
        info('\n****** parameter()', str(self.parameter), '\n')
        self.services = Services()
        info('\n****** services()', str(self.services), '\n')

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
        self.Switch02.clicked.connect(self.Switch02clicked)

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
        self.Link13.clicked.connect(self.Link12clicked)

        self.bpStartMN.clicked.connect(self.StartMNclicked)
        self.bpStopMN.clicked.connect(self.StopMNclicked)
        self.bpRestartMN.clicked.connect(self.RestartMNclicked)
        self.pbCLI.clicked.connect(self.CLIclicked)
        self.actionEnter_CLI.triggered.connect(self.CLIclicked)
        self.pbExit.clicked.connect(self.pbExitclicked)

        self.updateProcesses()

        self.cli_do.connect(self.CLIexecute)

        self.stopSystemServices()


    def StartMNclicked(self):
        self.instanceMN = MN()
        self.changeStatus("Start network...")
        self.instanceMN.startMN(MAC_random=self.cbRandomMAC.isChecked())
        self.changeStatus("Network started")


    def StopMNclicked(self):
        self.changeStatus("Stop network...")
        self.instanceMN.stopNet()
        self.changeStatus("Network stopped")

    def RestartMNclicked(self):
        self.StopMNclicked()
        self.StartMNclicked()

    def stopSystemServices(self):
#        return_code = subprocess.call("systemctl is-active NetworkManager", shell=True)
        return_descr = subprocess.Popen(["/bin/systemctl", "is-active", "NetworkManager"], stdout=subprocess.PIPE)
        (stdoutdata, stderrdata) = return_descr.communicate()
        if stdoutdata == "active\n":
# needed until this bug is fixed: https://github.com/mininet/mininet/issues/228
            print "beende NetworkManager"
            subprocess.call("systemctl stop NetworkManager", shell=True)
            subprocess.call("dhclient eth0", shell=True)

# or disable asterisk at startup
#        return_code = subprocess.call("systemctl is-active asterisk", shell=True)
        return_descr = subprocess.Popen(["/bin/systemctl", "is-active", "asterisk"], stdout=subprocess.PIPE)
        (stdoutdata, stderrdata) = return_descr.communicate()
        if stdoutdata == "active\n":
            subprocess.call("systemctl stop asterisk", shell=True)

# or disable vsftp at startup
#        return_code = subprocess.call("systemctl is-active vsftpd", shell=True)
        return_descr = subprocess.Popen(["/bin/systemctl", "is-active", "vsftpd"], stdout=subprocess.PIPE)
        (stdoutdata, stderrdata) = return_descr.communicate()
        if stdoutdata == "active\n":
            subprocess.call("systemctl stop vsftpd", shell=True)

    def CLIclicked(self):
# FIXME: Erzeuge ein Signal, dass dann die CLI aufruft.
#        self.changeStatus("GUI ist eingefroren bis die CLI mit \"exit\" beendet wurde!")
#        print "CLIclicked1"
        self.cli_do.emit()  #geht trotzdem nicht
# evtl mit postEvent, aber wie?
#        print "CLIclicked2"

    def CLIexecute(self):
#        print "CLIexecute1"
        mySW.instanceMN.startCLI()
#        print "CLIexecute2"

    def changeStatus(self, statusMessage):
#        print "changeStatus1"
        self.statusBar().showMessage(statusMessage)
#        print "changeStatus2"

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

        clist = ['Child 1', 'Child 2']
#        treeWidget=QtGui.QTreeWidget(self)
#        treeWidget.setGeometry(QtCore.QRect(50,50,150,140))
        tree.setHeaderLabels(["Host", "PID"])


        for parent in plist:
            pitems = QtGui.QTreeWidgetItem(tree)
            pitems.setText(0, parent)
            for child in clist:
                citems = QtGui.QTreeWidgetItem(pitems)
                citems.setText(0, child)


    def pbExitclicked(self):
        try:
            self.StopMNclicked()
        except:
            print "Mininet konnte nicht richtig beendet werden"
        exit(0)


    def bpStartMN_enabled(self, value):
        self.bpStartMN.setEnabled(value)

    def bpStopMN_enabled(self, value):
        self.bpStopMN.setEnabled(value)


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

    def showHostWindow(self, Hostnumber):
        myHost = HostConfig()
        info('\n*** myhost erzeugt\n')
#        print ("hostconfig vor show")
        myHost.listHost.setCurrentRow(Hostnumber - 1)  #FIXME
        info('\n****** host list auf erste,... gesetzt\n')
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
#        print "routerconfig vor show"
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


    def showSwitchWindow(self, Switchnumber):
        mySwitch = SwitchConfig()
#        print ("switchconfig vor show")
        mySwitch.listSwitch.setCurrentRow(Switchnumber - 1)
        mySwitch.exec_()

    def Switch01clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showSwitchWindow(1)

    def Switch02clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showSwitchWindow(2)

    def showLinkWindow(self, Linknumber):
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

    def Link13clicked(self):
        self.showLinkWindow(13)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
 #   setLogLevel( 'info' )
    mySW = ControlMainWindow()
    mySW.StartMNclicked()
#    myNode = NodeConfig()
    mySW.show()
#    myNode.show()
    sys.exit(app.exec_())
