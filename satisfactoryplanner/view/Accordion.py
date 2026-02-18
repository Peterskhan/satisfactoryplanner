from PySide6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal

class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class Accordion(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        
        # Header frame
        self.header = ClickableFrame()
        self.header.clicked.connect(self.toggle)
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addWidget(self.header)

        # Accordion icon
        self.icon = QLabel()
        self.icon.setPixmap(QPixmap(16, 16))
        self.header_layout.addWidget(self.icon)

        # Accordion title
        self.title_label = QLabel(title)
        self.header_layout.addWidget(self.title_label)

        # Stretch to push the toggle button to the right
        self.header_layout.addStretch()

        # Expand/collapse toggle button
        self.toggle_button = QPushButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setIcon(QIcon(QPixmap(16, 16)))
        self.toggle_button.setStyleSheet("QPushButton { border: none; }")
        self.toggle_button.clicked.connect(self.toggle)
        self.header_layout.addWidget(self.toggle_button)

        # Content area
        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.Shape.StyledPanel)
        self.main_layout.addWidget(self.content_area)
        self.on_toggle()

    def add_content(self, widget):
        """Add a widget to the accordion's content area."""
        content_layout = self.content_area.layout()
        if content_layout is None:
            content_layout = QVBoxLayout(self.content_area)
        content_layout.addWidget(widget)
        
    def toggle(self):
        self.toggle_button.setChecked(not self.toggle_button.isChecked())
        self.on_toggle()

    def on_toggle(self):
        if self.toggle_button.isChecked():
            self.content_area.show()
        else:
            self.content_area.hide()
    