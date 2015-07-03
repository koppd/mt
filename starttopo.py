#-*- coding: utf-8 -*-
import sys
#from PySide import QtGui
#from PySide import QtCore
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import uic

#from mainwindow import Ui_MainWindow


class HostConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(HostConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confHost.ui', self)
        print "hostconfig init...)"

        for host in mySW.getNodeList("Host"):
            self.listHost.addItem(host.objectName())

class RouterConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RouterConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confRouter.ui', self)
        print "confRouter init...)"

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


class LinkConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LinkConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confLink.ui', self)
        print "linkconfig init...)"

        for host in mySW.getNodeList("Link"):
            self.listLink.addItem(host.objectName())


class SwitchConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(SwitchConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('confSwitch.ui', self)
        print "linkSwitch init...)"

        for host in mySW.getNodeList("Switch"):
            self.listSwitch.addItem(host.objectName())



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


class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('topo.ui', self)


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

        self.pbExit.clicked.connect(self.pbExitclicked)

        self.updateProcesses()

#        self.debug1.clicked.connect(self.getHostList)


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

    def getNodeList(self, Nodetype):
        """ extract all children of QWidget TopoArea for a 
        certain type like Router, Host, Link, Switch
        Output: Host01, Host02, ... (as defined in Qt designer) """
        anyList = []
        lineEdits = self.TopoArea.findChildren(QtGui.QWidget)
        Nodetypelen = len(Nodetype)
        for i in lineEdits:
            if i.objectName()[:Nodetypelen] == Nodetype:
                anyList.append(i)

        listSorted = sorted(anyList, key=lambda temp: temp.objectName())
        for node in listSorted:
            print node.objectName()

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
        self.drawMultiLinesObj(qp, self.Router03, self.Host05, self.Host06)
# Bottom
        self.drawMultiLinesObj(qp, self.Router04, self.Router01, self.Router03)

        qp.end()

    def showHostWindow(self, Hostnumber) :
        myHost = HostConfig()
        print ("hostconfig vor show")
        myHost.exec_()
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
        print ("switchconfig vor show")
        mySwitch.exec_()

    def Switch01clicked(self):
#        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        self.showSwitchWindow(1)


    def showLinkWindow(self, Linknumber) :
        myLink = LinkConfig()
        print ("linkconfig vor show")
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
    mySW = ControlMainWindow()
#    myNode = NodeConfig()
    mySW.show()
#    myNode.show()
    sys.exit(app.exec_())
