from PySide6.QtWidgets import QGridLayout, QToolButton, QWidget, QScrollArea
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QSize
from collections import defaultdict
from slapp.resources.loader import ResourceLoader

from slapp.widgets import Accordion

class BuildingButton(QToolButton):

    def __init__(self, text: str, icon: QPixmap = None) -> None:
        super().__init__()
        self.setText(text)
        self.setIcon(QIcon(icon))
        self.setIconSize(QSize(32, 32))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setFixedSize(80, 80)

class BuildingPaletteWidget(QScrollArea):
    building_selected = Signal(object)

    def __init__(self, buildings, parent=None):
        super().__init__(parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Container
        self.accordion = Accordion()
        self.setWidget(self.accordion)
        self.setWidgetResizable(True)

        self.populate_buildings(buildings)
        self.setMinimumWidth(self.accordion.sizeHint().width())

    def populate_buildings(self, buildings):
        grouped = defaultdict(list)
        for b in buildings.values():
            grouped[b.category].append(b)

        for category, building_types in grouped.items():
            category_icon = QPixmap(ResourceLoader.load(':/icons/ResIcon_Production.webp')).scaled(32, 32)
            grid = QWidget()
            grid_layout = QGridLayout(grid)
            grid_layout.setAlignment(Qt.AlignLeft)

            for i, building_type in enumerate(building_types):
                building_icon = QPixmap(building_type.icon)
                button = BuildingButton(building_type.name, icon=building_icon)
                button.clicked.connect(lambda _, bt=building_type: self.building_selected.emit(bt))

                row = i // 3
                col = i % 3
                grid_layout.addWidget(button, row, col)

            self.accordion.add_section(category, grid, icon=category_icon)

        #for line_type in line_types.values():
        #    button = QPushButton(line_type.name)
        #    button.clicked.connect(lambda _, lt=line_type: self.building_selected.emit(lt))
        #    self.accordion_group.add_accordion(button)

