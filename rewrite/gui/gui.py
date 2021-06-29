from PyQt5 import QtWidgets, uic
import sys


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("gui/muonic4.ui", self)

        # Get buttons for open studies
        self.btOpenStudiesStop = self.findChild(
            QtWidgets.QPushButton, "btOpenStudiesStop"
        )
        self.btOpenStudiesStart = self.findChild(
            QtWidgets.QPushButton, "btOpenStudiesStart"
        )

        self.btOpenStudiesStart.clicked.connect(self.btOpenStudiesStartClicked)
        self.btOpenStudiesStop.clicked.connect(self.btOpenStudiesStopClicked)

        # Get values for open studies
        self.ckOpenStudiesCH0Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH0Enabled"
        )
        self.OpenStudiesCH0Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH0Voltage"
        )
        self.ckOpenStudiesCH1Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH1Enabled"
        )
        self.OpenStudiesCH1Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH1Voltage"
        )
        self.ckOpenStudiesCH2Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH2Enabled"
        )
        self.OpenStudiesCH2Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH2Voltage"
        )
        self.ckOpenStudiesCH3Enabled = self.findChild(
            QtWidgets.QCheckBox, "ckOpenStudiesCH3Enabled"
        )
        self.OpenStudiesCH3Voltage = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesCH3Voltage"
        )

        # Get radio buttons for open studies coincidence
        self.OpenStudiesSingleCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesSingleCoincidence"
        )
        self.OpenStudiesTwoFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesTwoFoldCoincidence"
        )
        self.OpenStudiesThreeFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesThreeFoldCoincidence"
        )
        self.OpenStudiesFourFoldCoincidence = self.findChild(
            QtWidgets.QRadioButton, "OpenStudiesFourFoldCoincidence"
        )

        # Get trigger window for open studies
        self.OpenStudiesTriggerWindow = self.findChild(
            QtWidgets.QSpinBox, "OpenStudiesTriggerWindow"
        )

        self.show()

    def btOpenStudiesStartClicked(self):
        print(
            f"Btn clicked {self.ckOpenStudiesCH0Enabled.isChecked()} -> {self.OpenStudiesCH0Voltage.text()}"
        )

    def btOpenStudiesStopClicked(self):
        print("Stop")


app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
