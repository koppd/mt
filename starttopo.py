#-*- coding: utf-8 -*-
import sys
#from PySide import QtGui
#from PySide import QtCore
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import uic

#from mainwindow import Ui_MainWindow


class NodeConfig(QtGui.QDialog):
    def __init__(self, parent=None):
        super(NodeConfig, self).__init__(parent)
#        super(ControlMainWindow, self).__init__(parent)
#        self.ui = Ui_MainWindow()
#        self.ui.setupUi(self)

        uic.loadUi('node.ui', self)
        print "nodeconfig init...)"


 

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

        self.pbExit.clicked.connect(self.pbExitclicked)

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

    def updateProcesses(self):
        tree = self.runningServices  # replace every 'tree' with your QTreeWidget
        plist = []        
        for i in range(1, 7):
            plist.append('Host '+str(i))
            
        clist=['Child 1','Child 2']
#        treeWidget=QtGui.QTreeWidget(self)
#        treeWidget.setGeometry(QtCore.QRect(50,50,150,140))
        tree.setHeaderLabels(["Node", "PID"])


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

        self.drawMultiLinesObj(qp, self.Router01, self.Host01, self.Host02, self.Host03)
        self.drawMultiLinesObj(qp, self.Router02, self.Host04, self.Router01, self.Router02, self.Router03, self.Router04)
        self.drawMultiLinesObj(qp, self.Router03, self.Host05, self.Host06)
        self.drawMultiLinesObj(qp, self.Router04, self.Router01, self.Router03)

        qp.end()
 
  
    def Host01clicked(self):
        myNode = NodeConfig()
        print ("nodeconfig vor show")
        myNode.exec_()
#        QtGui.QMessageBox.information(self, "Hello", "Host 1 clicked!")
        pass

    def Host02clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Host 2 clicked!")
        pass

    def Host03clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Host 3 clicked!")
        pass
    
    def Host04clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Host 4 clicked!")
        pass

    def Host05clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Host 5 clicked!")
        pass

    def Host06clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Host 6 clicked!")
        pass

    def Router01clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Router 1 clicked!")
        pass

    def Router02clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Router 2 clicked!")
        pass

    def Router03clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Router 3 clicked!")
        pass

    def Router04clicked(self):
        QtGui.QMessageBox.information(self, "Hello", "Router 4 clicked!")
        pass



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
#    myNode = NodeConfig()    
    mySW.show()
#    myNode.show()
    sys.exit(app.exec_())
