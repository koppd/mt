#-*- coding: utf-8 -*-
import sys
from PySide import QtCore, QtGui
from mainwindow import Ui_MainWindow
import TCPloss



class ControlMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
#old style
        #self.connect(self.ui.pushButton, QtCore.SIGNAL("clicked()"), self.btn1clicked)

#new style
        self.ui.pushButton.clicked.connect(self.btn1clicked)
  
    def btn1clicked(self):
        #QtGui.QMessageBox.information(self, "Hello", "Button 1 clicked!")
        TCPloss.myNetwork()
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = ControlMainWindow()
    mySW.show()
    sys.exit(app.exec_())
