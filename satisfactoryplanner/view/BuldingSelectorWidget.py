from PySide6.QtWidgets import QVBoxLayout, QGridLayout, QPushButton, QWidget, QScrollArea
from PySide6.QtGui import QPixmap
from collections import defaultdict
from PySide6.QtCore import Qt, Signal

from view.Accordion import Accordion

class BuildingPaletteWidget(QScrollArea):
    building_selected = Signal(object)

    def __init__(self, buildings, parent=None):
        super().__init__(parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.setWidget(self.container)
        self.setWidgetResizable(True)

        self.populate_buildings(buildings)

    def populate_buildings(self, buildings):
        grouped = defaultdict(list)
        for b in buildings:
            grouped[b.category].append(b)

        for category, building_types in grouped.items():
            accordion = Accordion(category)
            accordion.icon.setPixmap(QPixmap('./resources/ResIcon_Production.webp').scaled(32, 32))
            grid = QWidget()
            grid_layout = QGridLayout(grid)

            for i, building_type in enumerate(building_types):
                button = QPushButton(building_type.name)
                button.clicked.connect(lambda _, bt=building_type: self.building_selected.emit(bt))

                row = i // 3
                col = i % 3
                grid_layout.addWidget(button, row, col)

            accordion.add_content(grid)

            # Optional: expand by default
            accordion.toggle_button.setChecked(True)
            accordion.on_toggle()

            self.container_layout.addWidget(accordion)

