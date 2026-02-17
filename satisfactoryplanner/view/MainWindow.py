from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout
)
from ..view.BuldingSelectorWidget import BuildingPaletteWidget
from ..view.EditorView import EditorView
from ..model.building import building_types

from ..model.LayoutModel import LayoutModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Satisfactory Layout Planner")

        central = QWidget()
        layout = QHBoxLayout(central)

        self.palette = BuildingPaletteWidget(building_types)
        self.editor = EditorView(LayoutModel())

        self.palette.building_selected.connect(self.editor.scene().set_current_building)

        layout.addWidget(self.palette)
        layout.addWidget(self.editor)

        self.setCentralWidget(central)

        self.resize(1920, 1080)
