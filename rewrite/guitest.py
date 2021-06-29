from PyQt5 import QtWidgets, uic
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('gui/muonic4.ui', self)
        self.show()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
# app = QApplication([])
# window = QWidget()
# layout = QVBoxLayout()
# layout.addWidget(QPushButton('Top'))
# layout.addWidget(QPushButton('Bottom'))
# window.setLayout(layout)
# window.show()

# app.exec()
