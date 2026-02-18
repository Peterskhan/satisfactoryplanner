from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar
)
from view.BuldingSelectorWidget import BuildingPaletteWidget
from view.EditorView import EditorView
from model.building import building_types

from model.FactoryLayout import FactoryLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Satisfactory Layout Planner")

        central = QWidget()
        layout = QHBoxLayout(central)

        self.palette = BuildingPaletteWidget(building_types)
        self.editor = EditorView(FactoryLayout())

        self.palette.building_selected.connect(self.editor.scene().set_preview_type)

        layout.addWidget(self.palette)
        layout.addWidget(self.editor)

        self.setCentralWidget(central)

        status = QStatusBar()
        self.setStatusBar(status)
        self.label_left = QLabel("Ready")
        self.label_right = QLabel("No selection")
        status.addWidget(self.label_left)           # left side
        status.addPermanentWidget(self.label_right) # right-aligned
        self.editor.scene().mouse_scene_position_changed.connect(self.label_right.setText)

        self.resize(1920, 1080)
