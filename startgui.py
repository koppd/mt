#-*- coding: utf-8 -*-
import sys
from PySide import QtCore, QtGui
from mainwindow import Ui_MainWindow
import TCPloss
import dhcp
import ftp
import voip


class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
#old style
        #self.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.btn1clicked)

#new style
        self.ui.TCPloss_Step1.clicked.connect(self.tcp1clicked)
        self.ui.TCPloss_Step2.clicked.connect(self.tcp2clicked)
        self.ui.TCPloss_Exit.clicked.connect(self.tcpExitclicked)

        self.ui.DHCP_Step1.clicked.connect(self.dhcp1clicked)
        self.ui.DHCP_Step2.clicked.connect(self.dhcp2clicked)
        self.ui.DHCP_Exit.clicked.connect(self.dhcpExitclicked)

        self.ui.FTP_Step1.clicked.connect(self.ftp1clicked)
        self.ui.FTP_Step2.clicked.connect(self.ftp2clicked)
        self.ui.FTP_Exit.clicked.connect(self.ftpExitclicked)

        self.ui.VoIP_Step1.clicked.connect(self.voip1clicked)
        self.ui.VoIP_Step2.clicked.connect(self.voip2clicked)
        self.ui.VoIP_Exit.clicked.connect(self.voipExitclicked)

  
    def tcp1clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen = TCPloss.netTCPloss()
                
        self.scen.myNetwork( delay=self.ui.TCPloss_delay.value(), 
                          loss=self.ui.TCPloss_loss.value(), 
                          swin=self.ui.TCPloss_swin.value() )

    def tcp2clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.startDownload( )

    def tcpExitclicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.stopNet( )


    def dhcp1clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen = dhcp.netDHCP()
        
        self.scen.myNetwork( delay = self.ui.TCPloss_delay.value(), 
                       fresh_daemon_leases = self.ui.DHCP_daemon_leases.isChecked(), 
                       fresh_client_leases = self.ui.DHCP_client_leases.isChecked(),
                       MAC_random = self.ui.DHCP_random_MAC.isChecked() )
        
    def dhcp2clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.startClient( )

    def dhcpExitclicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.stopNet( )


    def ftp1clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen = ftp.netFTP()
        
        self.scen.myNetwork( delay = self.ui.FTP_delay.value(), 
                       pasv = self.ui.FTP_pasv.isChecked() )
        
    def ftp2clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.startDownload( )

    def ftpExitclicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.stopNet( )


    def voip1clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen = voip.netVoIP()
        
        self.scen.myNetwork( delay = self.ui.VoIP_delay.value())
        
    def voip2clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.startPhones( )

    def voipExitclicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
#        print self.ui.TCPloss_delay.value(), self.ui.TCPloss_loss.value(), self.ui.TCPloss_swin.value()
        self.scen.stopNet( )


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
