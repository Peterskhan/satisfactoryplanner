from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QToolButton, QGridLayout, QPushButton
)
from PySide6.QtCore import Qt, Signal


class CategorySectionWidget(QWidget):
    building_selected = Signal(object)

    def __init__(self, category_name, buildings, parent=None):
        super().__init__(parent)

        self.buildings = buildings

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Header button
        self.toggle_button = QToolButton()
        self.toggle_button.setText(category_name)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.clicked.connect(self.toggle_content)

        self.main_layout.addWidget(self.toggle_button)

        # Content widget
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)

        self._populate_buttons()

        self.main_layout.addWidget(self.content_widget)

    def _populate_buttons(self):
        columns = 3
        for i, building in enumerate(self.buildings):
            row = i // columns
            col = i % columns

            button = QPushButton(building.name)
            button.clicked.connect(
                lambda checked, b=building: self.building_selected.emit(b)
            )

            self.grid_layout.addWidget(button, row, col)

    def toggle_content(self):
        self.content_widget.setVisible(
            self.toggle_button.isChecked()
        )
