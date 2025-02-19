from PyQt5 import QtCore, QtGui, QtWidgets

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("test app")
        button = QPushButton("press")

        self.setCentralWidget(button)




app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()