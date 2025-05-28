from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.toggle_widgets = []
        
        # Header frame
        self.header_frame = QFrame()
        self.header_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toggle_button = QToolButton()
        self.toggle_button.setText("Aggregate Data Graphs")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        header_layout.addWidget(self.toggle_button, stretch=1)
        header_layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.header_frame)
        
        # Container for histograms
        self.hist_container = QWidget()
        self.hist_layout = QVBoxLayout(self.hist_container)
        self.hist_layout.setContentsMargins(0, 0, 0, 0)
        self.hist_container.setVisible(False)
        self.layout.addWidget(self.hist_container)
        
        # Connect toggle
        self.toggle_button.toggled.connect(self.toggle_histograms)
    
    def toggle_histograms(self, checked):
        self.hist_container.setVisible(checked)
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
    
    def display_histograms(self, df, column="Grade", bins=10):
        # Clear existing
        for i in reversed(range(self.hist_layout.count())):
            widget = self.hist_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Group by Question ID
        grouped = df.groupby("Question ID")
        
        for question_id, group in grouped:
            fig = Figure(figsize=(6, 4.5), dpi=100)
            canvas = FigureCanvas(fig)
            canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            canvas.setMinimumHeight(350)
            
            ax = fig.add_subplot(111)
            grades = group[column].dropna()
            ax.hist(grades, bins=bins, edgecolor='black', alpha=0.7)
            
            ax.set_title(f"Grade Distribution: {question_id.split(':')[0]}")
            ax.set_xlabel("Grade")
            ax.set_ylabel("Number of Students")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            
            self.hist_layout.addWidget(canvas)