import functions
from ai_client import get_ai_response, get_ai_response_2, set_model, MODEL_OPTIONS
from default_settings import AGGREGATE_PROMPT
from PyQt5.QtWidgets import QMessageBox
import pandas as pd


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

            question_id_full = df_encoded.columns[q_idx]

            if "\n" in question_id_full:
                question_id, question_text = question_id_full.split("\n", 1)
            else:
                question_id = question_id_full
                question_text = question_id_full

            try:
                ai_output = get_ai_response(csv_string, self.individual_prompt)
            except RuntimeError as e:
                QMessageBox.critical(self, "AI Error", f"Failed to get AI feedback:\n{str(e)}")
                continue 

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

                    # Fix Excel
                    if feedback_text.startswith(("=", "-", "+", "@")):
                        feedback_text = "'" + feedback_text

                    student_name = inverted.get(temp_id, temp_id)
                    if not feedback_text.strip():
                        status = "Missing"
                    elif len(feedback_text.split()) < 5:
                        status = "Incomplete"
                    else:
                        status = "Answered"

                    rows.append({
                        "Student Name": student_name,
                        "Question ID": question_id.strip(),
                    "Question Text": question_text.strip(),
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

        system_prompt = self.aggregate_prompt or AGGREGATE_PROMPT
        
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

