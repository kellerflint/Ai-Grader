from PyQt5 import QtCore, QtWidgets

import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow

from ai_client import get_ai_response

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Grader")
        
        # center widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)


        #layout for widget
        layout = QtWidgets.QHBoxLayout()
        central_widget.setLayout(layout)


        # align the buttons
        button = QtWidgets.QPushButton("Upload")
        layout.addWidget(button)
        button2 = QtWidgets.QPushButton("Submit")
        layout.addWidget(button2)
        button3 = QtWidgets.QPushButton("Ask AI")
        button3.clicked.connect(onClickAI)
        layout.addWidget(button3)

        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.resize(500, 300)

def onClickAI():
    print("Clicked")
    print(get_ai_response("Give this sentence a score A to F looking for any mistakes: 'How doot you do?'"))

app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
