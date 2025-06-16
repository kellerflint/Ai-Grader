import sys
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from app.storage.logs import get_log_dir, save_df_as_log, save_text_as_log
import pandas as pd
from .. import functions
from .ai_processing import get_aggregate_grades

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def upload_file(self):
        # Open a file dialog to select a CSV file
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")

        if file_path:
            self.file_path = file_path
            self.ask_ai_button.setEnabled(True)
            self.ask_ai_button.setToolTip("Click to submit file")
            QMessageBox.information(self, "File Uploaded", f"File uploaded successfully: {file_path}")

        # now that we have data, enable the submit button        
        self.on_file_uploaded()

def upload_feedback(self):
        # Open a file dialog to select a CSV file
        log_dir = get_log_dir("individual")
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open CSV File", log_dir, "CSV Files (*.csv)")

        if file_path:
            self.log_file_path = file_path
            QMessageBox.information(self, "File Uploaded", f"File uploaded successfully: {file_path}")
        else:
            QMessageBox.warning(self, "No File", "Please upload a CSV file first.")
        
        try:
            # Clear previous buttons if refreshing
            for i in reversed(range(self.student_layout.count())):
                widget_to_remove = self.student_layout.itemAt(i).widget()
                if widget_to_remove:
                    widget_to_remove.setParent(None)

            df = pd.read_csv(self.log_file_path)
            # save the df to the app for use with copy buttons
            self.structured_df = df

            individual_feedback_file_name = os.path.splitext(os.path.basename(self.log_file_path))[0]
            aggregate_feedback_file_path = get_log_dir("aggregate")
            aggregate_feedback_file_path = os.path.join(aggregate_feedback_file_path, f"{individual_feedback_file_name}.txt")
            
            aggregate_grades = ""
            try:
                with open(aggregate_feedback_file_path, 'r', encoding='utf-8') as file:
                    aggregate_grades = file.read()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
                if not os.path.exists(aggregate_feedback_file_path):
                    # rerun aggregate grades
                    aggregate_grades = "[Re-Submitted] " + get_aggregate_grades(self.structured_df, getattr(self, 'aggregate_prompt', None))
            
            self.display_aggregate_feedback(aggregate_grades)
            self.display_students()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")  

def on_file_uploaded(self):
                self.ask_ai_button.setEnabled(True)
                self.ask_ai_button.setStyleSheet("")  
                self.ask_ai_button.setToolTip("Click to submit")   

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
            from .ai_processing import generate_structured_feedback
            structured_df = generate_structured_feedback(df, question_indexes, idMap, self.individual_prompt)
            structured_path = os.path.join(
                os.path.dirname(self.file_path),
                "structured_feedback.csv"
            )
            structured_df.to_csv(structured_path, index=False)
            timestamp = save_df_as_log(structured_df)
            QMessageBox.information(
                self,
                "Structured Export",
                f"Structured feedback saved to: {structured_path}"
            )

            # save the df to the app for use with copy buttons
            self.structured_df = structured_df  
            # print(self.structured_df)
            aggregate_grades = get_aggregate_grades(self.structured_df, getattr(self, 'aggregate_prompt', None))

            #save aggregate grades
            save_text_as_log(aggregate_grades, timestamp)

            #display aggregate grades
            self.display_aggregate_feedback(aggregate_grades)
            self.display_students()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
