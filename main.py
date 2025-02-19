from PyQt5 import QtCore, QtGui, QtWidgets

from pathlib import Path

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Grader")

        # center widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)


        #layout for widget
        layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(layout)


        button = QtWidgets.QPushButton("Upload")
        layout.addWidget(button)

        layout.setAlignment(QtCore.Qt.AlignCenter)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
