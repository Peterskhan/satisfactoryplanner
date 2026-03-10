from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QLabel, QStatusBar, QVBoxLayout, QToolButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QPixmap
from slapp.editor.scene import EditorScene
from slapp.editor.view import EditorView
from slapp.core.discrete import building_types
from slapp.widgets.minimap import MinimapView
from slapp.widgets.build_select import BuildingPaletteWidget
from slapp.widgets.floorselector import FloorSelector
from slapp.widgets.menubar import Menubar
from slapp.resources.loader import ResourceLoader

class MainWindow(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.application = app
        self.setWindowTitle('Satisfactory Layout Planner')

        self.building_palette = BuildingPaletteWidget(building_types)
        self.scene = EditorScene(self)
        self.editor = EditorView(self.scene)

        self.scene.loaded_file_changed.connect(self.set_title)
        self.building_palette.building_selected.connect(self.editor.scene().set_preview_type)

        status = QStatusBar()
        self.setStatusBar(status)
        self.label_left = QLabel("Ready")
        self.label_right = QLabel("No selection")
        status.addWidget(self.label_left)           # left side
        status.addPermanentWidget(self.label_right) # right-aligned
        self.editor.scene().mouse_scene_position_changed.connect(self.label_right.setText)

        from slapp.editor.debug import SceneDebugWindow
        self.debug_window = SceneDebugWindow(self.scene)
        #self.debug_window.show()

        self.close_button = QToolButton()
        self.close_button.setIcon(QPixmap(ResourceLoader.load(':/icons/close.svg')))
        self.close_button.clicked.connect(self.close)
        self.create_menus()

        central = QWidget()
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.menu_bar)
        top_layout.addWidget(self.close_button)
        editor_layout = QHBoxLayout()
        editor_layout.addWidget(self.building_palette)
        editor_layout.addWidget(self.editor)
        main_layout = QVBoxLayout(central)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(editor_layout)
        self.setCentralWidget(central)

        self.minimap = MinimapView(self.editor, self)
        self.minimap.setFixedSize(200, 200)
        self.minimap.raise_()

        self.floor_selector = FloorSelector(self.scene, parent=self.editor)
        self.floor_selector.raise_()
        self.floor_selector.floor_changed.connect(self.scene.change_floor)
        self.scene.factory_changed.connect(self.floor_selector.refresh)

    def set_title(self, current_save_file: str | None) -> None:
        """Set the title of the window according to the current save file."""
        self.setWindowTitle(f'SLAPP - {current_save_file or "Untitled Factory"}')

    def create_menus(self) -> None:
        self.menu_bar = Menubar()
        #self.menu_bar = self.menuBar()

        # ===========================================================
        # File menu
        # ===========================================================
        self.file_menu = self.menu_bar.addMenu('File')

        self.new_action = self.file_menu.addAction('New')
        self.new_action.triggered.connect(self.scene.initialize_layout)
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

        # ===========================================================
        # View menu
        # ===========================================================
        self.view_menu = self.menu_bar.addMenu('View')

        self.toggle_grid_action = self.view_menu.addAction('Show Grid')
        self.toggle_grid_action.setCheckable(True)
        self.toggle_grid_action.setChecked(True)
        self.toggle_grid_action.toggled.connect(self.scene.set_grid_visible)

        self.toggle_minimap_action = self.view_menu.addAction('Show Minimap')
        self.toggle_minimap_action.setCheckable(True)
        self.toggle_minimap_action.setChecked(True)
        self.toggle_minimap_action.toggled.connect(self.set_minimap_visible)

    def set_minimap_visible(self, visible: bool) -> None:
        self.minimap.setVisible(visible)

    def resizeEvent(self, event):
        self.minimap.move(self.width() - self.minimap.width() - 30,
                          self.height() - self.minimap.height() - 50)
        self.minimap.fitInView(self.editor.scene().sceneRect(), Qt.KeepAspectRatio)

        ew = self.editor.viewport().width()
        eh = self.editor.height()
        self.floor_selector.move(ew - self.floor_selector.width(), eh - 400)

        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_T:
            with open(ResourceLoader.load(':/theme.qss'), mode='r') as theme_file:
                self.application.setStyleSheet(theme_file.read())

        return super().keyPressEvent(event)