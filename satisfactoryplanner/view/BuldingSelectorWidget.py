from PySide6.QtWidgets import QWidget, QVBoxLayout
from collections import defaultdict
from PySide6.QtCore import Qt, Signal
from ..view.CategorySectionWidget import CategorySectionWidget

class BuildingPaletteWidget(QWidget):
    building_selected = Signal(object)

    def __init__(self, buildings, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        grouped = defaultdict(list)
        for b in buildings:
            grouped[b.category].append(b)

        for category, items in grouped.items():
            section = CategorySectionWidget(category, items)
            section.building_selected.connect(
                self.building_selected
            )
            layout.addWidget(section)
