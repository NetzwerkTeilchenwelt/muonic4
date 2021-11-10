from lib.gui import gui
from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
window = gui.Ui()
app.exec_()
