from PyQt5.QtWidgets import QApplication, QStyle, QWidget, QGridLayout, QToolButton, QScrollArea, QPushButton, QMainWindow, \
    QFileDialog, QMessageBox, QTextEdit, QLabel, QLineEdit, QDialog, QHBoxLayout, QVBoxLayout
from functools import partial
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt
from pathlib import Path
import sys
import pandas as pd
from ai_client import get_ai_response, get_ai_response_2
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
        
        # submit button
        self.ask_ai_button = QPushButton("Submit")
        self.ask_ai_button.setFixedWidth(300)
        self.ask_ai_button.setFixedHeight(50)
        self.ask_ai_button.clicked.connect(self.process_file)
        layout.addWidget(self.ask_ai_button, 0, 2, 1, 1, Qt.AlignTop)
        
        # faq button
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

        # settings button
        right_hbox = QHBoxLayout()
        right_hbox.setContentsMargins(0, 0, 0, 0)
        right_hbox.addWidget(self.settingsButton)
        right_hbox.addWidget(self.faqButton)
        layout.addLayout(right_hbox, 0,3,1,2, Qt.AlignRight)

        # place for feedback
        self.feedback_area = QScrollArea()
        self.feedback_area.setWidgetResizable(True)
        self.content = QWidget()
        self.scroll_layout = QVBoxLayout(self.content)
        self.feedback_area.setWidget(self.content)
        layout.addWidget(self.feedback_area, 2, 0, 1, 5) 

        self.resize(1000, 800)

        # Store the file path
        self.file_path = None

    def display_students(self):
        # Clear previous buttons if refreshing (this will cause issues for any widgets 
        # added in other methods, so we should move it elsewhere)
        # for i in reversed(range(self.scroll_layout.count())):
        #   widget_to_remove = self.scroll_layout.itemAt(i).widget()
        #   if widget_to_remove:
        #       widget_to_remove.setParent(None)

        # check if there is a dataframe to pull from
        if not hasattr(self, 'structured_df') or self.structured_df is None:
            return

        # Group feedback by student name
        grouped = self.structured_df.groupby("Student Name")
        all_questions = self.structured_df["Question ID"].unique()

        # for each student's data, arrange the box to show
        for student_name, group in grouped:

            # Create a container widget to hold responses
            container = QWidget()
            h_layout = QHBoxLayout(container)

            # force student name to be a string and prevent errors
            label = QLabel(str(student_name))
            label.setFixedWidth(150)

            # display the feedback
            text_edit = QTextEdit()
            text_edit.setReadOnly(True)
            text_edit.setMinimumHeight(100)

            feedback_map = dict(zip(group["Question ID"], zip(group["Feedback"], group["Status"])))

            # Highlight unanswered or incomplete
            feedback = ""
            copy_text = ""
            for question in all_questions:
                if question in feedback_map:
                    answer, status = feedback_map[question]
                    if status in ["Missing", "Incomplete"]:
                        feedback += f"⚠️ {question}: (Missing or incomplete response)\n\n"
                        copy_text += "(Missing or incomplete response)"
                    else:
                        feedback += f"{question}:\n{answer}\n\n"
                        copy_text += f"{answer}\n\n"
                else:
                    feedback += f"⚠️ {question}: (No response submitted)\n\n"
                    copy_text += "(No response submitted)"

            text_edit.setPlainText(feedback)

            # add the copy button for each student feedback
            copy_button = QToolButton()
            copy_button.setObjectName("copyButton")
            copy_button.setIcon(qta.icon('fa5s.copy'))
            copy_button.setText("Copy")
            copy_button.setToolTip(f"Copy feedback for {student_name}")
            copy_button.clicked.connect(partial(self.copy_specific_feedback, copy_text))

            # Add widgets to the layout
            h_layout.addWidget(label)
            h_layout.addWidget(text_edit)
            h_layout.addWidget(copy_button)

            # add container with all the data
            self.scroll_layout.addWidget(container)

    def copy_specific_feedback(self, feedback_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(feedback_text)
        print(f"Copied feedback: {feedback_text}")

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
                print("AI Output:", repr(feedback)) 


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

            # save the df to the app for use with copy buttons
            self.structured_df = structured_df  
            # print(self.structured_df)
            aggregate_grades = self.get_aggregate_grades()
            self.display_aggregate_feedback(aggregate_grades)
            self.display_students()

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

                    if not feedback_text.strip():
                        status = "Missing"
                    elif len(feedback_text.split()) < 5:
                        status = "Incomplete"
                    else:
                        status = "Answered"
                    rows.append({
                        "Student Name": student_name,
                        "Question ID": df_encoded.columns[q_idx],
                        "Grade": grade,
                        "Feedback": feedback_text,
                        "Status": status
                    })

        return pd.DataFrame(rows)
    
    def get_aggregate_grades(self):
        # Filter out rows where feedback is too short
        filtered_df = self.structured_df[self.structured_df['Feedback'].str.len() > 10]

        # Group by Question ID and store each group in a dictionary
        question_dfs = {qid: group.reset_index(drop=True) for qid, group in filtered_df.groupby('Question ID')}

        aggregate_feedback = [
            "Aggregate Feedback: "
        ]

        system_prompt = """You are an AI grader assistant. I will give you a list of student feedback and grades for a single question. Please provide:

1. A brief summary of the feedback trends across students.
2. Suggestions for how students could improve their answers.
3. The average grade.
"""
        
        # Access each DataFrame by Question ID
        for qid, qdf in question_dfs.items():
            #generate user prompt based on grades and feedback
            user_prompt = functions.format_aggregate_prompt(qid, qdf)
            aggregate_feedback.append(f"\n{qid}\n")

            #pass system and user prompt into AI
            ai_response = get_ai_response_2(system_prompt, user_prompt)
            aggregate_feedback.append(ai_response)

        aggregate_feedback = '\n'.join(aggregate_feedback)
        return aggregate_feedback

    def display_aggregate_feedback(self, feedback):
        # Create a container widget to hold responses
        container = QWidget()
        h_layout = QHBoxLayout(container)

        # display the feedback
        text_edit = QTextEdit()
        text_edit.setPlainText(feedback)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(100)

        # Add widgets to the layout
        h_layout.addWidget(text_edit)

        # add container with all the data
        self.scroll_layout.addWidget(container)

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