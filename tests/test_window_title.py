from main import MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import sys

import unittest

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()


class test(unittest.TestCase):
    def test_window_title_name(self):
        self.assertEqual(window.windowTitle(), "AI Grader")


if __name__ == "__main__":
    unittest.main()
