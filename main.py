from PyQt5 import QtCore, QtGui, QtWidgets

from pathlib import Path

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ai Grader ")
        button = QPushButton("Upload ")

        self.setCentralWidget(button)




app = QApplication(sys.argv)
app.setStyleSheet(Path('styles/styles.qss').read_text())

window = MainWindow()
window.show()

app.exec_()