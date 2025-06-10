from PyQt5.QtWidgets import (
    QDialog, QLabel, QPushButton, QLineEdit, QComboBox,
    QTextEdit, QGridLayout, QMessageBox, QMainWindow
)
import os

from default_settings import PROMPT, AGGREGATE_PROMPT
from api_key_functions import load_api_key, save_api_key
from prompt_store import (
    save_prompt, load_prompts,
    save_aggregate_prompt, load_aggregate_prompts
)
from ai_client import MODEL_OPTIONS, set_model

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
        self.current_key_label = QLabel(f"Current OpenRouter API Key: {load_api_key() or 'Not set'}")
        layout.addWidget(self.current_key_label)

        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "LLaMA 3.3 8B (Free)",
            "LLaMA 3 70B (Free)",
            "Mixtral 8x7B (Free)",
            "Claude 3 Haiku (Free)",
            "Gemma 7B (Free)",
            "OpenChat 3.5 (Free)"
        ])
        current_label = os.getenv("DEFAULT_MODEL", "LLaMA 3.3 8B (Free)")
        self.model_selector.setCurrentText(current_label)
        self.model_display = QLabel()
        layout.addWidget(self.model_display)
        self.model_display.setText(f"Current Model: {MODEL_OPTIONS[current_label]}")
        layout.addWidget(QLabel("Select Model:"))
        layout.addWidget(self.model_selector)

        self.model_selector.currentTextChanged.connect(self.update_model_selection)

        # Input field for new API key
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter new OpenRouter API key")
        layout.addWidget(self.input_field)

        # Save button
        save_button = QPushButton("Save API Key")
        save_button.clicked.connect(self.save_new_api_key)
        layout.addWidget(save_button, 2, 0, 1, 2)

        # --- New prompt settings section ---
        # Label for the prompt name input
        prompt_name_label = QLabel("Individual Prompt Name:")
        layout.addWidget(prompt_name_label, 3, 0, 1, 2)

        # Input field for new prompt name
        self.prompt_name_input = QLineEdit()
        self.prompt_name_input.setPlaceholderText("Enter name for this prompt")
        layout.addWidget(self.prompt_name_input, 4, 0, 1, 2)

        # Input field for new prompt
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter prompt template here...")
        self.prompt_edit.setFixedHeight(100)
        layout.addWidget(self.prompt_edit, 5, 0, 1, 2)

        # Save button for prompt input
        save_prompt_button = QPushButton("Save Individual Prompt")
        save_prompt_button.clicked.connect(self.save_prompt_template)
        layout.addWidget(save_prompt_button, 6, 0, 1, 2)

        # Dropdown for existing saved prompts (read-only list)
        dropdown_name_label = QLabel("Select Individual Custom Prompt:")
        layout.addWidget(dropdown_name_label, 7, 0, 1, 2)
        self.prompt_dropdown = QComboBox()
        self.prompt_dropdown.setPlaceholderText("Saved Prompts")
        layout.addWidget(self.prompt_dropdown, 8, 0, 1, 2)

        # Load the latest prompt if available
        self.load_prompts_into_dropdown()

        # Red "Update Prompt" button
        update_prompt_button = QPushButton("Update Individual Prompt")
        update_prompt_button.setStyleSheet("background-color: blue; color: white;")
        layout.addWidget(update_prompt_button, 9, 0, 1, 2)
        update_prompt_button.clicked.connect(self.update_selected_prompt)

        # --- Aggregate prompt settings section ---
        aggregate_name_label = QLabel("Aggregate Prompt Name:")
        layout.addWidget(aggregate_name_label, 10, 0, 1, 2)

        self.aggregate_name_input = QLineEdit()
        self.aggregate_name_input.setPlaceholderText("Enter name for this aggregate prompt")
        layout.addWidget(self.aggregate_name_input, 11, 0, 1, 2)

        self.aggregate_prompt_edit = QTextEdit()
        self.aggregate_prompt_edit.setPlaceholderText("Enter aggregate prompt template here...")
        self.aggregate_prompt_edit.setFixedHeight(100)
        layout.addWidget(self.aggregate_prompt_edit, 12, 0, 1, 2)

        save_agg_button = QPushButton("Save Aggregate Prompt")
        save_agg_button.clicked.connect(self.save_aggregate_prompt_template)
        layout.addWidget(save_agg_button, 13, 0, 1, 2)

        aggregate_dropdown_name_label = QLabel("Select Aggregate Custom Prompt:")
        layout.addWidget(aggregate_dropdown_name_label, 14, 0, 1, 2)
        self.aggregate_prompt_dropdown = QComboBox()
        self.aggregate_prompt_dropdown.setPlaceholderText("Saved Aggregate Prompts")
        layout.addWidget(self.aggregate_prompt_dropdown, 15, 0, 1, 2)

        update_agg_button = QPushButton("Update Aggregate Prompt")
        update_agg_button.setStyleSheet("background-color: blue; color: white;")
        update_agg_button.clicked.connect(self.update_aggregate_prompt)
        layout.addWidget(update_agg_button, 16, 0, 1, 2)

        self.load_aggregate_prompts_into_dropdown()

    def save_new_api_key(self):
        new_key = self.input_field.text().strip()
        if not new_key:
            QMessageBox.warning(self, "Invalid Input", "API key cannot be empty.")
            return
        save_api_key(new_key)
        QMessageBox.information(self, "Success", "API key updated.")
        self.current_key_label.setText(f"Current API Key: {new_key}")
        self.input_field.clear()


    #Individual prompt functions
    def save_prompt_template(self):
        prompt_name = self.prompt_name_input.text().strip()
        prompt_content = self.prompt_edit.toPlainText().strip()

        if not prompt_name or not prompt_content:
            QMessageBox.warning(self, "Invalid Input", "Both prompt name and content are required.")
            return

        new_prompt = {"name": prompt_name, "content": prompt_content}
        save_prompt(new_prompt)

        QMessageBox.information(self, "Success", "Prompt template saved.")

        self.prompt_name_input.clear()
        self.prompt_edit.clear()
        #Remember the name of the prompt just saved
        saved_name = prompt_name

        self.load_prompts_into_dropdown()

        #Reselect the saved prompt
        index = self.prompt_dropdown.findText(saved_name)
        if index != -1:
            self.prompt_dropdown.setCurrentIndex(index)
            self.on_prompt_selected(index)


    def load_prompts_into_dropdown(self):
        from default_settings import PROMPT as default_prompt

        try:
            self.prompt_dropdown.currentIndexChanged.disconnect()
        except TypeError:
            pass

        self.prompt_dropdown.clear()
        self.prompt_map = {}

        #Add the default prompt as the first item
        default_name = "[Default Prompt]"
        self.prompt_map[default_name] = default_prompt
        self.prompt_dropdown.addItem(default_name)

        #Add all user saved prompts
        prompts = load_prompts()
        for prompt in prompts:
            name = prompt["name"]
            content = prompt["content"]
            self.prompt_map[name] = content
            self.prompt_dropdown.addItem(name)

        self.prompt_dropdown.currentIndexChanged.connect(self.on_prompt_selected)
         #Force default to be selected and populated
        self.prompt_dropdown.setCurrentIndex(0)
        self.on_prompt_selected(0)

    def on_prompt_selected(self, index):
        if index >= 0:
            name = self.prompt_dropdown.itemText(index)
            content = self.prompt_map.get(name, "")

            # Update editor field with selected prompt
            self.prompt_edit.setPlainText(content)

            # Pass selected prompt to main window
            if isinstance(self.parent(), QMainWindow):
                if name == "[Default Prompt]":
                    self.parent().set_individual_prompt(None)
                else:
                    self.parent().set_individual_prompt(content)

            print(f"[Prompt Selected] Now using: {name}")


    def update_selected_prompt(self):
        name = self.prompt_dropdown.currentText()
        updated_content = self.prompt_edit.toPlainText().strip()

         #Prevent saving the default prompt
        if name == "[Default Prompt]":
            if isinstance(self.parent(), QMainWindow):
                self.parent().set_individual_prompt(None)
            QMessageBox.information(self, "Default Selected", "Default prompt is now active. It will not be saved.")
            return

        if not name:
            QMessageBox.warning(self, "No Selection", "Please select a prompt to update.")
            return

        if not updated_content:
            QMessageBox.warning(self, "Default Prompt", "Prompt is empty. Default prompt will be used.")
            if isinstance(self.parent(), QMainWindow):
                self.parent().set_individual_prompt(None)
            return

        # Save the updated content
        updated_prompt = {"name": name, "content": updated_content}
        save_prompt(updated_prompt)

        # Send it back to MainWindow
        if isinstance(self.parent(), QMainWindow):
            self.parent().set_individual_prompt(updated_content)

        #print to show confirmation of the prompt being used
        print("\n[Prompt Update] Prompt selected for individual grading:")    
        print(updated_content or "[No prompt selected — will use default PROMPT]")

        QMessageBox.information(self, "Success", f"Prompt '{name}' updated and applied.")

        updated_name = name
        self.load_prompts_into_dropdown()

        index = self.prompt_dropdown.findText(updated_name)
        if index != -1:
            self.prompt_dropdown.setCurrentIndex(index)
            self.on_prompt_selected(index)

        #Aggregate prompt functions
    def load_aggregate_prompts_into_dropdown(self):
        try:
            self.aggregate_prompt_dropdown.currentIndexChanged.disconnect()
        except TypeError:
            pass  # It wasn’t connected yet

        self.aggregate_prompt_dropdown.clear()
        self.aggregate_prompt_map = {}

        #Default prompt
        default_name = "[Default Aggregate Prompt]"
        self.aggregate_prompt_map[default_name] = AGGREGATE_PROMPT
        self.aggregate_prompt_dropdown.addItem(default_name)

        prompts = load_aggregate_prompts()
        for prompt in prompts:
            name = prompt["name"]
            content = prompt["content"]
            self.aggregate_prompt_map[name] = content
            self.aggregate_prompt_dropdown.addItem(name)

        self.aggregate_prompt_dropdown.currentIndexChanged.connect(self.on_aggregate_prompt_selected)

        #Force default to be selected and populated
        self.aggregate_prompt_dropdown.setCurrentIndex(0)
        self.on_aggregate_prompt_selected(0)

    def save_aggregate_prompt_template(self):
        name = self.aggregate_name_input.text().strip()
        content = self.aggregate_prompt_edit.toPlainText().strip()

        if not name or not content:
            QMessageBox.warning(self, "Invalid Input", "Both name and prompt content are required.")
            return

        new_prompt = {"name": name, "content": content}
        save_aggregate_prompt(new_prompt)
        QMessageBox.information(self, "Saved", "Aggregate prompt saved successfully.")

        self.aggregate_name_input.clear()
        self.aggregate_prompt_edit.clear()
        saved_name = name
        self.load_aggregate_prompts_into_dropdown()

        index = self.aggregate_prompt_dropdown.findText(saved_name)
        if index != -1:
            self.aggregate_prompt_dropdown.setCurrentIndex(index)
            self.on_aggregate_prompt_selected(index)

    def update_aggregate_prompt(self):
        name = self.aggregate_prompt_dropdown.currentText()
        content = self.aggregate_prompt_edit.toPlainText().strip()

        #Prevent saving the default aggregate prompt
        if name == "[Default Aggregate Prompt]":
            if isinstance(self.parent(), QMainWindow):
                self.parent().set_aggregate_prompt(None)
            QMessageBox.information(self, "Default Selected", "Default aggregate prompt is now active. It will not be saved.")
            return    

        if not name:
            QMessageBox.warning(self, "No Selection", "Please select a prompt to update.")
            return
        if not content:
            QMessageBox.warning(self, "Invalid Content", "Prompt content cannot be empty.")
            return

        updated_prompt = {"name": name, "content": content}
        save_aggregate_prompt(updated_prompt)

        # Pass back to main window
        if isinstance(self.parent(), QMainWindow):
            self.parent().set_aggregate_prompt(content)

        # Print for validation
        print("\n[Prompt Update] Prompt selected for AGGREGATE grading:")
        print(content or "[No prompt selected — will use default aggregate prompt]")    

        QMessageBox.information(self, "Updated", f"Aggregate prompt '{name}' updated and applied.")
        updated_name = name
        self.load_aggregate_prompts_into_dropdown()

        index = self.aggregate_prompt_dropdown.findText(updated_name)
        if index != -1:
            self.aggregate_prompt_dropdown.setCurrentIndex(index)
            self.on_aggregate_prompt_selected(index)

    def on_aggregate_prompt_selected(self, index):
        if index >= 0:
            name = self.aggregate_prompt_dropdown.itemText(index)
            content = self.aggregate_prompt_map.get(name, "")
            self.aggregate_prompt_edit.setPlainText(content)

            if isinstance(self.parent(), QMainWindow):
                if name == "[Default Aggregate Prompt]":
                    self.parent().set_aggregate_prompt(None)
                else:
                    self.parent().set_aggregate_prompt(content)
            # Print prompt name and content for validation
            print(f"[Prompt Selected] Now using AGGREGATE prompt: {name}")

    def update_model_selection(self, selected_text):
        try:
            set_model(selected_text)
            self.model_display.setText(f"Current Model: {MODEL_OPTIONS[selected_text]}")
        except ValueError as e:
            QMessageBox.warning(self, "Model Error", str(e))