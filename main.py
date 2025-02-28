from PyQt5 import QtCore, QtWidgets

from pathlib import Path

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow

from ai_client import get_ai_response

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Grader")
        
        # center widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)


        #layout for widget
        layout = QtWidgets.QGridLayout()
        central_widget.setLayout(layout)

        # create and align the buttons
        layout.setContentsMargins(0, 50, 0, 0)
        button = QPushButton("Upload")
        button.setFixedWidth(300)
        button.setFixedHeight(50)
        layout.addWidget(button,0, 0, 1, 1, QtCore.Qt.AlignTop)

        button2 = QPushButton("Submit")
        button2.setFixedWidth(300)
        button2.setFixedHeight(50)
        layout.addWidget(button2, 0, 2, 1, 1, QtCore.Qt.AlignTop)

        button3 = QPushButton("Ask AI")
        button3.clicked.connect(onClickAI)
        button3.setFixedWidth(300)
        button3.setFixedHeight(50)
        layout.addWidget(button3, 0, 3, 1, 1, QtCore.Qt.AlignTop)

        self.resize(1000, 800)

def onClickAI():
    print("Clicked")
    print(get_ai_response("Give this sentence a score A to F looking for any mistakes: 'How doot you do?'"))

app = QApplication(sys.argv)

app.setStyleSheet(Path('./styles/styles.qss').read_text())
window = MainWindow()
window.show()

app.exec_()
