from PyQt5 import QtCore, QtWidgets

import sys

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

        layout.setAlignment(QtCore.Qt.AlignCenter)
        self.resize(500, 300)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
