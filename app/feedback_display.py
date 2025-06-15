from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolButton, QSizePolicy, QApplication
import qtawesome as qta
from PyQt5.QtCore import Qt
from functools import partial
from display_histograms import HistogramWidget
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.figure import Figure

def display_students(self):
        # Check dataframe exists
        if not hasattr(self, 'structured_df') or self.structured_df is None:
            return

        section_label = QLabel("Individual Student Grades")
        section_label.setStyleSheet("font-weight: bold; font-size: 20px; margin: 10px 0;")
        self.student_layout.addWidget(section_label)

        self.expand_all_button.clicked.connect(self.toggle_all_sections)
        self.expand_all_button.setToolTip("Expand all")
        self.expand_all_button.setEnabled(True)
        self.expand_all_button.setIcon(qta.icon('fa6s.caret-down', color="black"))

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
            body_widget = QLabel()
            body_widget.setText(feedback)
            body_widget.setWordWrap(True)
            body_widget.setVisible(False)
            body_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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

def display_aggregate_feedback(self, feedback):
        # Parse feedback into a dictionary
        feedback_blocks = feedback.strip().split("\n")
        summaries = {}
        current_qid = None
        current_lines = []

        for line in feedback_blocks:
            if line.strip() in self.structured_df["Question ID"].unique():
                if current_qid and current_lines:
                    summaries[current_qid] = "\n".join(current_lines).strip()
                current_qid = line.strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_qid and current_lines:
            summaries[current_qid] = "\n".join(current_lines).strip()

        # Main container for toggle
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        toggle_button = QToolButton()
        toggle_button.setText("Aggregate Data")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.setArrowType(Qt.RightArrow)
        toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(toggle_button)

        summary_container = QWidget()
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setContentsMargins(0, 0, 0, 0)

        grouped = self.structured_df.groupby("Question ID")
        for question_id, group in grouped:

            # single histogram per question
            histogram_widget = HistogramWidget.create_histogram_widget(group, column="Grade", bins=10)
            summary_layout.addWidget(histogram_widget)

            feedback_text = summaries.get(question_id, "No feedback available.")
            feedback_label = QLabel(feedback_text)
            feedback_label.setWordWrap(True)
            summary_layout.addWidget(feedback_label)

        summary_container.setVisible(False)

        def toggle_body(checked):
            summary_container.setVisible(checked)
            toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)

        toggle_button.toggled.connect(toggle_body)

        layout.addWidget(header_frame)
        layout.addWidget(summary_container)
        self.student_layout.addWidget(container)
        self.toggle_widgets.append((toggle_button, summary_container))            

def create_histograms(self, layout, df, column="Grade", bins=10):
        # Clear any existing histograms
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Group by Question ID
        grouped = df.groupby("Question ID")
        
        for question_id, group in grouped:
            # Create a figure and canvas
            fig = Figure(figsize=(10, 8), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            
            # Extract grades and plot histogram
            grades = group[column].dropna()
            ax.hist(grades, bins=bins, edgecolor='black', alpha=0.7)
            
            # Customize the plot
            ax.set_title(f"Grade Distribution: {question_id.split(':')[0]}", wrap=True)
            ax.set_xlabel("Grade")
            ax.set_ylabel("Number of Students")
            ax.grid(True, alpha=0.3)
            
            # Adjust layout
            fig.tight_layout()
            
            # Add to the layout
            layout.addWidget(canvas)            

def toggle_all_sections(self):
        expand = self.expand_all_button.isChecked()
        self.expand_all_button.setToolTip("Collapse All" if expand else "Expand All")

        for toggle_button, body_widget in self.toggle_widgets:
            body_widget.setVisible(expand)
            toggle_button.setArrowType(Qt.DownArrow if expand else Qt.RightArrow)
            toggle_button.setChecked(expand)

            body_widget.adjustSize()
            if body_widget.parent():
                body_widget.parent().adjustSize()  

        # update all the button icons
        self.expand_all_button.setToolTip("Collapse all" if expand else "Expand all")
        icon = qta.icon('fa6s.caret-up' if expand else 'fa6s.caret-down', color="black")
        self.expand_all_button.setIcon(icon)
        
        # force app to process so our sections collapse to the correct size
        # Force layout update
        self.feedback_widget.updateGeometry()
        self.feedback_widget.adjustSize()
        
        # Process events and ensure proper sizing
        QApplication.processEvents()
        self.centralWidget().updateGeometry() 

def copy_specific_feedback(self, feedback_text):
        clipboard = QApplication.clipboard()
        clipboard.setText(str(feedback_text))                   