import os
import sys
import pandas as pd
from io import StringIO
from functools import partial
from PyQt5.QtWidgets import QApplication, QStyle, QWidget, QGridLayout, QToolButton, QScrollArea, QPushButton, \
    QMainWindow, \
    QFileDialog, QMessageBox, QTextEdit, QLabel, QLineEdit, QDialog, QHBoxLayout, QVBoxLayout, QFrame, QSpacerItem, \
    QSizePolicy, QComboBox
from PyQt5.QtGui import QClipboard, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox
import qtawesome as qta
from pathlib import Path
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.figure import Figure

from app.ai.ai_client import get_ai_response, get_ai_response_2, set_model, MODEL_OPTIONS
from app.ai.api_key_functions import load_api_key, save_api_key
from app.display.display_histograms import HistogramWidget
from app.storage.logs import save_df_as_log, save_text_as_log, get_log_dir
from app import functions
from app.storage.prompt_store import save_prompt, load_prompts, save_aggregate_prompt, load_aggregate_prompts
from app.ai.default_settings import AGGREGATE_PROMPT
from app.display.settings_dialog import SettingsDialog
from app.display.file_handlers import resource_path
from app.display.ai_processing import parse_ai_response, generate_structured_feedback, get_aggregate_grades, sanitize_for_excel
from app.display.file_handlers import upload_file, upload_feedback, on_file_uploaded,process_file
from app.display.feedback_display import display_students, display_aggregate_feedback, copy_specific_feedback, toggle_all_sections, show_faq, open_settings_dialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.toggle_widgets = []

        # Bind imported functions to this instance
        self.upload_file = upload_file.__get__(self)
        self.upload_feedback = upload_feedback.__get__(self)
        self.process_file = process_file.__get__(self)
        self.on_file_uploaded = on_file_uploaded.__get__(self)
        self.display_students = display_students.__get__(self)
        self.display_aggregate_feedback = display_aggregate_feedback.__get__(self)
        self.copy_specific_feedback = copy_specific_feedback.__get__(self)
        self.toggle_all_sections = toggle_all_sections.__get__(self)
        self.show_faq = show_faq.__get__(self)
        self.open_settings_dialog = open_settings_dialog.__get__(self)

        #allows sylesheets to be found and applied
        styles_path = resource_path('styles/styles.qss')
        self.setStyleSheet(Path(styles_path).read_text())


        self.setWindowTitle("AI Grader")
        
        # Center widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout for widget
        layout = QGridLayout()
        self.model_display = QLabel()
        layout.addWidget(self.model_display)
        central_widget.setLayout(layout)

        # Create and align the buttons
        layout.setContentsMargins(0, 50, 0, 0)

        # history menu
        self.history_button = QPushButton()
        self.history_button.setObjectName("historyButton")
        self.history_button.setIcon(qta.icon('fa6s.folder-open'))
        self.history_button.setFixedSize(50, 50)
        self.history_button.clicked.connect(self.upload_feedback)
        layout.addWidget(self.history_button, 0, 0, Qt.AlignTop)

        # upload button
        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedWidth(300)
        self.upload_button.setFixedHeight(50)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button, 0, 1, 1, 1, Qt.AlignTop)
        
        # submit button, disabled until file is uploaded
        self.ask_ai_button = QPushButton("Submit")
        self.ask_ai_button.setFixedWidth(300)
        self.ask_ai_button.setFixedHeight(50)
        self.ask_ai_button.setToolTip("Upload a file to submit!")
        self.ask_ai_button.setEnabled(False)
        self.ask_ai_button.setStyleSheet("background-color: lightgray; color: gray;")
        self.ask_ai_button.clicked.connect(self.process_file)
        layout.addWidget(self.ask_ai_button, 0, 2, 1, 1, Qt.AlignTop)

        # expand all button
        self.expand_all_button = QPushButton()
        self.expand_all_button.setCheckable(True)
        self.expand_all_button.setObjectName("expandButton")
        self.expand_all_button.clicked.connect(self.toggle_all_sections)
        self.expand_all_button.clicked.disconnect()
        self.expand_all_button.setToolTip("Cannot expand until information is processed")
        self.expand_all_button.setIcon(qta.icon('fa6s.caret-down', color='lightgray'))
        
        # faq button
        self.faqButton = QPushButton()
        self.faqButton.setObjectName("faqButton")
        self.faqButton.clicked.connect(self.show_faq)
        self.faqButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.faqButton.resize(self.faqButton.sizeHint())

        # Settings Menu
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setIcon(qta.icon('mdi.cog'))
        self.settingsButton.clicked.connect(self.open_settings_dialog)

        # settings button
        right_hbox = QHBoxLayout()
        right_hbox.setContentsMargins(0, 0, 0, 0)
        right_hbox.addWidget(self.expand_all_button)
        right_hbox.addWidget(self.settingsButton)
        right_hbox.addWidget(self.faqButton)
        layout.addLayout(right_hbox, 0,3,1,2, Qt.AlignRight)

        # place for feedback
        self.feedback_widget = QWidget()
        self.student_layout = QVBoxLayout(self.feedback_widget)
        self.feedback_widget.setLayout(self.student_layout)

        # Wrap feedback_widget in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.feedback_widget)

        layout.addWidget(scroll_area, 2, 0, 1, 5)

        self.resize(1000, 800)

        # Store file paths
        self.file_path = None

        # Holds the latest user-defined individual grading prompt
        self.individual_prompt = None  

        # Holds the latest user-defined aggregate grading prompt
        self.aggregate_prompt = None

    #Setter for individual prompt
    def set_individual_prompt(self, prompt_text):
        self.individual_prompt = prompt_text

    #Setter for aggregate prompt
    def set_aggregate_prompt(self, prompt_text):
        self.aggregate_prompt = prompt_text    


        self.log_file_path = None

    def sanitize_for_excel(self, text):
        unwanted_prefixes = ('=', '+', '-', '@')
        lines = text.splitlines()
        safe_lines = []
        for line in lines:
            if line.strip().startswith(unwanted_prefixes):
                safe_lines.append("'" + line) 
            else:
                safe_lines.append(line)
        return '\n'.join(safe_lines)
    

    def show_faq(self, event):
        msg = QMessageBox()  # 'msg' is the QMessageBox, not the faqButton
        msg.setIcon(QMessageBox.Information)
        msg.setText("How To Use This App:")
        msg.setInformativeText("1. Click the upload file button. \n"
        "2. Upload your csv, which should follow the standard Canvas\n"
        "output format. \n"
        "3. Click submit and your request will be sent to the AI. \n"
        "4. Your results will then print below the buttons for your use.")
        msg.setWindowTitle("Usage Guide")

        msg.buttonClicked.connect(self.msgbtn) 

        retval = msg.exec_()  # Execute the message box
        print("value of pressed message box button:" + str(retval)) 

    def msgbtn(self, btn):
        print("FAQ Exited:", btn.text())


    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()