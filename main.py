from tkinter.simpledialog import SimpleDialog

from PyQt5 import QtCore, QtWidgets
# noinspection LongLine
from PyQt5.QtWidgets import QApplication, QStyle, QWidget, QPushButton, QMainWindow, QFileDialog, QMessageBox, QTextEdit, QDialog
from PyQt5.QtGui import QClipboard
from pathlib import Path
import sys
import pandas as pd
from ai_client import get_ai_response
import os
import functions
from io import StringIO

#bundles file pathing that allows exe to work or python command to work
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #allows sylesheets to be found and applied
        styles_path = resource_path('styles/styles.qss')
        app.setStyleSheet(Path(styles_path).read_text())

        self.setWindowTitle("AI Grader")
        
        # Center widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for widget
        layout = QtWidgets.QGridLayout()
        central_widget.setLayout(layout)

        # Create and align the buttons
        layout.setContentsMargins(20, 30, 20, 20)

        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedWidth(300)
        self.upload_button.setFixedHeight(50)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button, 0, 0, 1, 1, QtCore.Qt.AlignTop)
        

        self.ask_ai_button = QPushButton("Submit")
        self.ask_ai_button.setFixedWidth(300)
        self.ask_ai_button.setFixedHeight(50)
        self.ask_ai_button.clicked.connect(self.process_file)
        layout.addWidget(self.ask_ai_button, 0, 2, 1, 1, QtCore.Qt.AlignTop)
        
        self.faqButton = QPushButton()
        self.faqButton.setObjectName("faqButton")
        self.faqButton.clicked.connect(self.show_faq)
        self.faqButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.faqButton.resize(self.faqButton.sizeHint())
        layout.addWidget(self.faqButton, 0, 4, 1, 1, QtCore.Qt.AlignRight)

        # Settings Menu
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setText("Settings")
        self.settingsButton.clicked.connect(self.open_settings_dialog)
        layout.addWidget(self.settingsButton, 0, 3, 1, 1, QtCore.Qt.AlignRight)

        # AI Response Box
        self.feedback_area = QTextEdit()
        self.feedback_area.setReadOnly(True)
        layout.addWidget(self.feedback_area, 1, 0, 1, 5)

        # Text Copy Box
        self.copyButton = QPushButton("Copy Text")
        self.copyButton.clicked.connect(self.copy_text)
        layout.addWidget(self.copyButton)

        self.resize(1000, 800)

        # Store the file path
        self.file_path = None

    def onClickAI(self):
        print("Clicked")
        question = "Question: What is 2 + 2?\n Student 1: 3\n Student 2: 4\n Student 3: Not sure"
        feedback = get_ai_response(question)
        self.feedback_area.append(feedback)

    def copy_text(self):
        text_to_copy = self.feedback_area.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)
        print(f"Copied to clipboard: {text_to_copy}")

    def upload_file(self):
        # Open a file dialog to select a CSV file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.file_path = file_path
            QMessageBox.information(self, "File Uploaded", f"File uploaded successfully: {file_path}")

    def process_file(self):
        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please upload a CSV file first.")
            return

        try:
            # Read the CSV file
            df = pd.read_csv(self.file_path, encoding='windows-1252')
            # Map student ids to temp ids
            idMap = functions.createIdMap(df["id"])

            # Encode ids
            df = functions.useMapEncode(df, idMap)

            # Split df for the first question
            new_df = functions.splitDfByQuestion(df, 9)
            # print("Split df: ")
            # print(new_df)
            # print(new_df[new_df.columns[1]])

            csv_buffer = StringIO()
            new_df.to_csv(csv_buffer, index=False)  # Writing to the buffer instead of a file

            # Get the CSV content as a string
            csv_string = csv_buffer.getvalue()

            # new_df.to_csv
            feedback = get_ai_response(csv_string)
            # print(feedback)
            self.feedback_area.append(feedback)

            # Process the data (Replace with AI)
            # df['is_correct'] = df['response'].apply(lambda x: x.strip().lower() == "the capital of france is paris.")

            # Decode ids
            df = functions.useMapDecode(df, idMap)
            print("Decoded IDs: ")
            print(df["id"])

            # Save the processed data to a new CSV file in the same directory as the uploaded file
            output_file_path = os.path.join(os.path.dirname(self.file_path), "processed_results.csv")
            df.to_csv(output_file_path, index=False)

            # Notify the user that the file has been saved
            QMessageBox.information(self, "File Saved", f"Processed file saved successfully: {output_file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def show_faq(self, event):
        msg = QMessageBox()  
        msg.setIcon(QMessageBox.Information)
        msg.setText("How To Use This App:")
        msg.setInformativeText("1. Click the upload file button. \n"
        "2. Upload your csv, which should follow the standard Canvas\n"
        "output format. \n"
        "3. Click submit and your request will be sent to the AI. \n"
        "4. Your results will then print below the buttons for your use.")
        msg.setWindowTitle("Usage Guide")

        msg.buttonClicked.connect(self.msgbtn) 

        retval = msg.exec_()

    # This is required for the faq button to work correctly
    def msgbtn(self, btn):
        print("FAQ Exited:", btn.text())


    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

        print("click")



class SettingsDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

# Run the application
app = QApplication(sys.argv)

#app.setStyleSheet(Path('./styles/styles.qss').read_text())
window = MainWindow()
window.show()

app.exec_()