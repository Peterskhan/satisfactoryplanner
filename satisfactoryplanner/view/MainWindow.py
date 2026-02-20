from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar, QGraphicsView
)
from PySide6.QtCore import Qt
from view.EditorScene import EditorScene
from view.BuldingSelectorWidget import BuildingPaletteWidget
from view.EditorView import EditorView
from view.Minimap import MinimapView
from model.BuldingInstance import building_types
from model.FactoryLayout import FactoryLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Satisfactory Layout Planner")

        central = QWidget()
        layout = QHBoxLayout(central)

        self.building_palette = BuildingPaletteWidget(building_types)
        self.factory = FactoryLayout()
        self.scene = EditorScene(self, self.factory)
        self.editor = EditorView(self.scene)

        self.building_palette.building_selected.connect(self.editor.scene().set_preview_type)

        layout.addWidget(self.building_palette)
        layout.addWidget(self.editor)
        self.setCentralWidget(central)

        self.minimap = MinimapView(self.editor, self)
        self.minimap.setFixedSize(200, 200)
        self.minimap.raise_()

        status = QStatusBar()
        self.setStatusBar(status)
        self.label_left = QLabel("Ready")
        self.label_right = QLabel("No selection")
        status.addWidget(self.label_left)           # left side
        status.addPermanentWidget(self.label_right) # right-aligned
        self.editor.scene().mouse_scene_position_changed.connect(self.label_right.setText)

        self.create_menus()

    def create_menus(self):
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu('File')
        self.file_new_action = self.file_menu.addAction('New')
        self.file_open_action = self.file_menu.addAction('Open')
        self.file_save_action = self.file_menu.addAction('Save')
        self.file_exit_action = self.file_menu.addAction('Exit')

        self.edit_menu = self.menu_bar.addMenu('Edit')
        self.edit_cut_action = self.edit_menu.addAction('Cut')
        self.edit_copy_action = self.edit_menu.addAction('Copy')
        self.edit_paste_action = self.edit_menu.addAction('Paste')

        self.configure_actions()

    def configure_actions(self):
        self.file_new_action.triggered.connect(lambda: None)
        self.file_open_action.triggered.connect(self.scene.load_layout_from_file)
        self.file_save_action.triggered.connect(self.scene.save_layout_to_file)
        self.file_exit_action.triggered.connect(self.close)

        self.edit_cut_action.triggered.connect(self.scene.cut_current_selection)
        self.edit_copy_action.triggered.connect(self.scene.copy_current_selection)
        self.edit_paste_action.triggered.connect(self.scene.paste_current_selection)

    def resizeEvent(self, event):
        self.minimap.move(self.width() - self.minimap.width() - 30,
                          self.height() - self.minimap.height() - 50)
        self.minimap.fitInView(self.editor.scene().sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)
