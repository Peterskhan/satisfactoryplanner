from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from slapp.editor.scene import EditorScene
from slapp.editor.view import EditorView
from slapp.core.discrete import building_types
from slapp.core.factory import FactoryLayout
from slapp.editor.widgets.minimap import MinimapView
from slapp.editor.widgets.build_select import BuildingPaletteWidget

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

        self.scene.loaded_file_changed.connect(self.set_title)

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
        self.scene.new_layout()

    def set_title(self, current_save_file: str | None) -> None:
        """Set the title of the window according to the current save file."""
        self.setWindowTitle(f'SLAPP - {current_save_file or "Untitled Factory"}')

    def create_menus(self):
        self.menu_bar = self.menuBar()

        # ===========================================================
        # File menu
        # ===========================================================
        self.file_menu = self.menu_bar.addMenu('File')

        self.new_action = self.file_menu.addAction('New')
        self.new_action.triggered.connect(self.scene.new_layout)
        self.new_action.setShortcut(QKeySequence.StandardKey.New)

        self.file_menu.addSeparator()

        self.open_action = self.file_menu.addAction('Open')
        self.open_action.triggered.connect(self.scene.load_layout_from_file)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)

        self.file_menu.addSeparator()

        self.save_action = self.file_menu.addAction('Save')
        self.save_action.triggered.connect(self.scene.save_layout_to_file)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)

        self.save_as_action = self.file_menu.addAction('Save As...')
        self.save_as_action.triggered.connect(self.scene.save_layout_to_file_as)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)

        self.file_menu.addSeparator()

        self.exit_action = self.file_menu.addAction('Exit')
        self.exit_action.triggered.connect(self.close)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Close)

        # ===========================================================
        # Edit menu
        # ===========================================================
        self.edit_menu = self.menu_bar.addMenu('Edit')

        self.cut_action = self.edit_menu.addAction('Cut')
        self.cut_action.triggered.connect(self.scene.cut_current_selection)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)

        self.copy_action = self.edit_menu.addAction('Copy')
        self.copy_action.triggered.connect(self.scene.copy_current_selection)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)

        self.paste_action = self.edit_menu.addAction('Paste')
        self.paste_action.triggered.connect(self.scene.paste_current_selection)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)

        self.edit_menu.addSeparator()

        self.select_all_action = self.edit_menu.addAction('Select All')
        self.select_all_action.triggered.connect(self.scene.select_all_items)
        self.select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)

        self.edit_menu.addSeparator()

        self.cancel_action = self.edit_menu.addAction('Cancel')
        self.cancel_action.triggered.connect(self.scene.cancel_current_operation)
        self.cancel_action.setShortcut(QKeySequence.StandardKey.Cancel)

        self.delete_action = self.edit_menu.addAction('Delete')
        self.delete_action.triggered.connect(self.scene.delete_current_selection)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)

        self.edit_menu.addSeparator()

        self.rotate_action = self.edit_menu.addAction('Rotate')
        self.rotate_action.triggered.connect(self.scene.rotate_current)
        self.rotate_action.setShortcut('R')

        # ===========================================================
        # Tools menu
        # ===========================================================
        self.build_menu = self.menu_bar.addMenu('Tools')

        self.conveyor_action = self.build_menu.addAction('Build Conveyor')
        self.conveyor_action.triggered.connect(self.scene.build_conveyor)
        self.conveyor_action.setShortcut('C')

        self.measure_action = self.build_menu.addAction('Measure...')
        self.measure_action.triggered.connect(self.scene.start_measurement)
        self.measure_action.setShortcut('M')

    def resizeEvent(self, event):
        self.minimap.move(self.width() - self.minimap.width() - 30,
                          self.height() - self.minimap.height() - 50)
        self.minimap.fitInView(self.editor.scene().sceneRect(), Qt.KeepAspectRatio)
        super().resizeEvent(event)
