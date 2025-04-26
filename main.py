from PyQt5.QtWidgets import QApplication, QStyle, QWidget, QGridLayout, QToolButton, QPushButton, QMainWindow, \
    QFileDialog, QMessageBox, QTextEdit, QLabel, QLineEdit, QDialog, QHBoxLayout
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import QTimer, Qt
from pathlib import Path
import sys
import pandas as pd
from ai_client import get_ai_response
from api_key_functions import load_api_key, save_api_key
import os
import functions
from io import StringIO
import qtawesome as qta

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
        layout = QGridLayout()
        central_widget.setLayout(layout)

        # Create and align the buttons
        layout.setContentsMargins(0, 50, 0, 0)

        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedWidth(300)
        self.upload_button.setFixedHeight(50)
        self.upload_button.clicked.connect(self.upload_file)
        layout.addWidget(self.upload_button, 0, 0, 1, 1, Qt.AlignTop)
        

        self.ask_ai_button = QPushButton("Ask AI")
        self.ask_ai_button.setFixedWidth(300)
        self.ask_ai_button.setFixedHeight(50)
        self.ask_ai_button.clicked.connect(self.process_file)
        layout.addWidget(self.ask_ai_button, 0, 2, 1, 1, Qt.AlignTop)
        
        self.faqButton = QPushButton()
        self.faqButton.setObjectName("faqButton")
        self.faqButton.clicked.connect(self.show_faq)
        self.faqButton.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.faqButton.resize(self.faqButton.sizeHint())
        # layout.addWidget(self.faqButton, 0, 4, 1, 1, Qt.AlignRight)

        # Settings Menu
        self.settingsButton = QPushButton()
        self.settingsButton.setObjectName("settingsButton")
        self.settingsButton.setIcon(qta.icon('mdi.cog'))
        self.settingsButton.clicked.connect(self.open_settings_dialog)
        # layout.addWidget(self.settingsButton, 0, 3, 1, 1, Qt.AlignRight)

        right_hbox = QHBoxLayout()
        right_hbox.setContentsMargins(0, 0, 0, 0)
        right_hbox.addWidget(self.settingsButton)
        right_hbox.addWidget(self.faqButton)
        layout.addLayout(right_hbox, 0,3,1,2, Qt.AlignRight)

        # AI Response Box
        self.feedback_area = QTextEdit()
        self.feedback_area.setReadOnly(True)
        layout.addWidget(self.feedback_area, 1, 0, 1, 5)

        # Text Copy Box
        self.copyButton = QToolButton(self.feedback_area.viewport())
        self.copyButton.setObjectName("copyButton")
        self.copyButton.setIcon(qta.icon('fa5s.copy'))
        self.original_resize_event = self.feedback_area.resizeEvent
        self.feedback_area.resizeEvent = self.new_resize_event
        self.copyButton.clicked.connect(self.copy_text)
        QTimer.singleShot(0, self.reposition_copy_button)

        self.resize(1000, 800)

        # Store the file path
        self.file_path = None

    def copy_text(self):
        # column_data = self.df['Grade'].toList()
        # text_to_copy = "\n".join(map(str, column_data))
        text_to_copy = self.feedback_area.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)
        print(f"Copied to clipboard: {text_to_copy}")

    def reposition_copy_button(self, event=None):
        margin = 25 
        x = self.feedback_area.width() - self.copyButton.width() - margin
        y = margin
        self.copyButton.move(x, y)

    def new_resize_event(self, event):
        self.original_resize_event(event)
        self.reposition_copy_button(event)

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
            df = pd.read_csv(self.file_path)

            # Map student ids to temp ids
            idMap = functions.createIdMap(df["id"])
            df = functions.useMapEncode(df, idMap)

            # Get all question columns
            question_indexes = functions.findQuestionIndexes(df)
            
            # Process each question
            for q_idx in question_indexes:
                # Get single question df
                question_df = functions.splitDfByQuestion(df, q_idx)
                
                # Get AI feedback
                csv_buffer = StringIO()
                question_df.to_csv(csv_buffer, index=False)
                # Get the CSV content as a string
                csv_string = csv_buffer.getvalue()

                # new_df.to_csv
                feedback = get_ai_response(csv_string)
            
                self.feedback_area.append(feedback)


            # Decode ids and save original df
            df = functions.useMapDecode(df, idMap)
            output_path = os.path.join(os.path.dirname(self.file_path), "processed_results.csv")
            df.to_csv(output_path, index=False)
            
            QMessageBox.information(self, "Complete", f"Evaluated {len(question_indexes)} questions\nResults saved to: {output_path}")

            # builds the dataframe will add more comment later
            structured_df = self.generate_structured_feedback(df, question_indexes, idMap)
            structured_path = os.path.join(
                os.path.dirname(self.file_path),
                "structured_feedback.csv"
            )
            structured_df.to_csv(structured_path, index=False)
            QMessageBox.information(
                self,
                "Structured Export",
                f"Structured feedback saved to: {structured_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def parse_ai_response(self, response):
        try:
            parts = response.split('Grade:')
            # everything before “Grade:” is the feedback text
            feedback_text = parts[0].strip()
            # everything after “Grade:” is the number grade
            grade = float(parts[1].strip())
            return grade, feedback_text
        except:
            return None, response

    # dataframe using temp ids for names
    def generate_structured_feedback(self, df_encoded, question_indexes, idMap):
        inverted = {v: k for k, v in idMap.items()}
        rows = []

        for q_idx in question_indexes:
            question_df = functions.splitDfByQuestion(df_encoded, q_idx)
            csv_string = question_df.to_csv(index=False)
            ai_output = get_ai_response(csv_string)

            # split on the '---' lines to get each feedback piece
            blocks = [b.strip() for b in ai_output.split('---') if b.strip()]
            for block in blocks:
                lines = block.splitlines()
                id_line = next((l for l in lines if l.startswith("ID:")), None)
                grade_line = next((l for l in lines if l.startswith("Grade:")), None)
                if id_line and grade_line:
                    temp_id = int(id_line.split("ID:")[1].strip())
                    grade = float(grade_line.split("Grade:")[1].strip())
                    # leftover lines are the bullet‐point feedback
                    feedback_lines = [l for l in lines if not l.startswith(("ID:", "Grade:"))]
                    feedback_text = "\n".join(feedback_lines).strip()

                    student_name = inverted.get(temp_id, temp_id)
                    rows.append({
                        "Student Name": student_name,
                        "Question ID": df_encoded.columns[q_idx],
                        "Grade": grade,
                        "Feedback": feedback_text
                    })

        return pd.DataFrame(rows)
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

        print("click")



class SettingsDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        # Layout for widget
        layout = QGridLayout()
        self.setLayout(layout)

        # Create and align the buttons
        #layout.setContentsMargins(20, 30, 20, 20)

        # Current API Key display
        self.current_key_label = QLabel(f"Current API Key: {load_api_key() or 'Not set'}")
        layout.addWidget(self.current_key_label)

        # Input field for new API key
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter new API key")
        layout.addWidget(self.input_field)

        # Save button
        save_button = QPushButton("Save API Key")
        save_button.clicked.connect(self.save_new_api_key)
        layout.addWidget(save_button)

    def save_new_api_key(self):
        new_key = self.input_field.text().strip()
        if not new_key:
            QMessageBox.warning(self, "Invalid Input", "API key cannot be empty.")
            return
        save_api_key(new_key)
        QMessageBox.information(self, "Success", "API key updated.")
        self.current_key_label.setText(f"Current API Key: {new_key}")
        self.input_field.clear()

# Run the application
app = QApplication(sys.argv)

#app.setStyleSheet(Path('./styles/styles.qss').read_text())
window = MainWindow()
window.show()

app.exec_()