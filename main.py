from PyQt5.QtWidgets import QApplication, QStyle, QWidget, QGridLayout, QToolButton, QScrollArea, QPushButton, QMainWindow, \
    QFileDialog, QMessageBox, QTextEdit, QLabel, QLineEdit, QDialog, QHBoxLayout, QVBoxLayout, QFrame, QSpacerItem, QSizePolicy
from functools import partial
from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt
from pathlib import Path
import sys
import pandas as pd
from ai_client import get_ai_response, get_ai_response_2
from api_key_functions import load_api_key, save_api_key
from logs import save_df_as_log
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

        # history menu
        self.history_button = QPushButton()
        self.history_button.setObjectName("historyButton")
        self.history_button.setIcon(qta.icon('fa6s.bars'))
        self.history_button.setFixedSize(50, 50)
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
        self.ask_ai_button.clicked.connect(self.process_file)
        layout.addWidget(self.ask_ai_button, 0, 2, 1, 1, Qt.AlignTop)

        # load button
        self.load_button = QPushButton("Load")
        self.load_button.setFixedWidth(100)
        self.load_button.setFixedHeight(50)
        self.load_button.clicked.connect(self.upload_feedback)
        layout.addWidget(self.load_button, 0, 3, 1, 1, Qt.AlignTop)

        # expand all button
        self.expand_all_button = QPushButton()
        self.expand_all_button.setCheckable(True)
        self.expand_all_button.setObjectName("expandButton")
        self.expand_all_button.clicked.connect(self.toggle_all_sections)
        self.ask_ai_button.setEnabled(False)
        self.expand_all_button.setToolTip("Expand or collapse all")
        self.expand_all_button.setIcon(qta.icon('fa6s.caret-down'))
        
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
        layout.addWidget(self.feedback_widget, 2, 0, 1, 5) 

        self.resize(1000, 800)

        # Store the file path
        self.file_path = None

    def display_students(self):
        # Check dataframe exists
        if not hasattr(self, 'structured_df') or self.structured_df is None:
            return

        self.expand_all_button.setEnabled(True)

        grouped = self.structured_df.groupby("Student Name")
        all_questions = self.structured_df["Question ID"].unique()

        for student_name, group in grouped:
            # Build feedback text for student
            feedback_map = dict(zip(group["Question ID"], zip(group["Feedback"], group["Status"])))
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

           # Collapsible Sections
            section_widget = QWidget()
            section_layout = QVBoxLayout(section_widget)
            section_layout.setContentsMargins(0, 0, 0, 0)
            section_layout.setSpacing(5)

            # Header button (collapsible + copy button)
            header_frame = QFrame()
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(0, 0, 0, 0)

            # Expand/Collapse button
            toggle_button = QToolButton()
            toggle_button.setText(str(student_name))
            toggle_button.setCheckable(True)
            toggle_button.setChecked(False)
            toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            toggle_button.setArrowType(Qt.RightArrow)
            toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

            # Body (feedback text)
            body_widget = QTextEdit()
            body_widget.setReadOnly(True)
            body_widget.setPlainText(feedback)
            body_widget.setVisible(False)

            # Copy button
            copy_button = QToolButton()
            copy_button.setIcon(qta.icon('fa5s.copy'))
            copy_button.setToolTip(f"Copy feedback for {student_name}")
            copy_button.clicked.connect(partial(self.copy_specific_feedback, copy_text))
            
            header_layout.addWidget(toggle_button)
            header_layout.addWidget(copy_button)

            section_layout.addWidget(header_frame)
            section_layout.addWidget(body_widget)

            # Toggle behavior
            def toggle_body(checked, button=toggle_button, body=body_widget):
                body.setVisible(checked)
                button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)


            toggle_button.toggled.connect(toggle_body)
            self.toggle_widgets.append((toggle_button, body_widget))

            # Add to main layout
            self.student_layout.addWidget(section_widget)
            self.student_layout.update()
            
    def toggle_all_sections(self):
        expand = self.expand_all_button.isChecked()
        self.expand_all_button.setText("Collapse All" if expand else "Expand All")

        for toggle_button, body_widget in self.toggle_widgets:
            toggle_button.setChecked(expand)

    # add a specified section of text to the clipboard
    def copy_specific_feedback(self, feedback_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(str(feedback_text))

    def upload_file(self):
        # Open a file dialog to select a CSV file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.file_path = file_path
            self.ask_ai_button.setEnabled(True)
            self.ask_ai_button.setToolTip("Click to submit file")
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
            save_df_as_log(structured_df)
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

    def upload_feedback(self):
        self.upload_file()

        if not self.file_path:
            QMessageBox.warning(self, "No File", "Please upload a CSV file first.")
            return
        
        try:
            # Clear previous buttons if refreshing
            for i in reversed(range(self.student_layout.count())):
                widget_to_remove = self.student_layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)

            df = pd.read_csv(self.file_path)
            # save the df to the app for use with copy buttons
            self.structured_df = df

            # rerun and display aggregate grades
            # TODO: save and load csv function for aggregate grades to prevent rerun
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
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(5)

        self.toggle_widgets = []

        # header for aggregate data
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)

        toggle_button = QToolButton()
        toggle_button.setText("Class Summary")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toggle_button.setArrowType(Qt.RightArrow)
        toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        text_edit = QTextEdit()
        text_edit.setPlainText(feedback)
        text_edit.setReadOnly(True)
        text_edit.setMinimumHeight(100)
        text_edit.setVisible(False)

        header_layout.addWidget(toggle_button)
        header_frame.setLayout(header_layout)
        self.toggle_widgets.append((toggle_button, text_edit))

        v_layout.addWidget(header_frame)
        v_layout.addWidget(text_edit)

        def toggle_aggregate_body(checked, body=text_edit, button=toggle_button):
            body.setVisible(checked)
            button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

        toggle_button.toggled.connect(toggle_aggregate_body)

        self.student_layout.addWidget(container)

        # add container with all the data
        self.student_layout.addWidget(container)

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