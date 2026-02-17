from PySide6.QtWidgets import QGraphicsScene, QFileDialog
from PySide6.QtCore import Qt, QPointF, QRectF
from ..view.Settings import Settings
from ..view.BuildingItem import BuildingItem
from ..model.building import BuildingType
from ..model.LayoutModel import LayoutModel, Position, Rotation, type_lookup
from enum import Enum

class SceneOperation(Enum):
    BUILDING_PLACEMENT = 1
    BUILDING_REMOVAL = 2

class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    operation: SceneOperation
    current_building_type: BuildingType
    ghost_item: BuildingItem

    def __init__(self, parent, layout_model: LayoutModel):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.current_building_type = None
        self.ghost_item = None
        self.layout_model = layout_model
        self.save_file = None
        self.operation = None
        self.last_mouse_scene_pos = None

    ## ======================================================
    ## Slots
    ## ====================================================== 

    def set_current_building(self, building_type):
        self.current_building_type = building_type
        self.operation = SceneOperation.BUILDING_PLACEMENT

        # This is a hack, because the view does not have focus to handle rotation events
        self.views()[0].setFocus()
        self.create_ghost()

    ## ======================================================
    ## Helper methods
    ## ======================================================

    def _place_building(self, pos):
        grid = Settings.PIXELS_PER_METER
        x = round(pos.x() / grid) * grid
        y = round(pos.y() / grid) * grid

        instance = self.layout_model.add_building(
            self.current_building_type,
            Position(x, y),
            self.ghost_item.instance.rotation
        )
        self.addItem(BuildingItem(instance))

    def create_ghost(self):
        if self.ghost_item:
            self.removeItem(self.ghost_item)

        self.ghost_item = BuildingItem(self.layout_model.create_building(self.current_building_type, Position(0, 0), Rotation.DEG_0))
        self.ghost_item.setOpacity(0.4)
        self.ghost_item.setZValue(9999)  # always on top

        self.addItem(self.ghost_item)

    def rotate_preview(self):
        self.ghost_item.instance.rotation = self.ghost_item.instance.rotation.rotate_clockwise()
        self.ghost_item.setRotation(self.ghost_item.instance.rotation.value * 90)
        self.snap_preview_to_cursor()

    def calculate_rotated_offset(self, item: BuildingItem) -> QPointF:
        if item.instance.rotation == Rotation.DEG_0:
            return QPointF(item.instance.type.width, item.instance.type.length) * Settings.PIXELS_PER_METER / 2.0
        elif item.instance.rotation == Rotation.DEG_90:
            return QPointF(-item.instance.type.length, item.instance.type.width) * Settings.PIXELS_PER_METER / 2.0
        elif item.instance.rotation == Rotation.DEG_180:
            return QPointF(-item.instance.type.width, -item.instance.type.length) * Settings.PIXELS_PER_METER / 2.0
        else:
            return QPointF(item.instance.type.length, -item.instance.type.width) * Settings.PIXELS_PER_METER / 2.0

    def snap_preview_to_cursor(self):
        if self.ghost_item is not None:
            offset = self.calculate_rotated_offset(self.ghost_item)
            self.ghost_item.setPos(self.last_mouse_scene_pos - offset)

    def delete_current_selection(self):
        for item in self.selectedItems():
            self.layout_model.remove_building(item.instance)
            self.removeItem(item)

    def select_all_items(self):
        for item in self.items():
            item.setSelected(True)

    def copy_current_selection(self):
        pass

    def cut_current_selection(self):
        pass

    def paste_current_selection(self):
        pass

    def save_layout_to_file(self):
        if self.save_file is None:
            self.save_file, _ = QFileDialog.getSaveFileName(
                None,
                'Save file',
                'factory.fl',
                'Factory layouts (*.fl)'
            )

        if self.save_file is None:
            return
        
        with open(self.save_file, mode='w') as save_file:
            save_file.write(self.layout_model.serialize())

    def load_layout_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            'Open file',
            '',
            'Factory layouts (*.fl)'
        )

        if file_name is None:
            return
        
        with open(file_name, mode='r') as load_file:
            json_str = load_file.read()
            self.layout_model.deserialize(json_str, type_lookup)

        # Clear existing items
        for item in self.items():
            self.removeItem(item)

        # Add items from the loaded layout
        for building in self.layout_model.buildings:
            self.addItem(BuildingItem(building))

    ## ======================================================
    ## Event handlers
    ## ======================================================

    def mousePressEvent(self, event):
        if self.operation == SceneOperation.BUILDING_PLACEMENT:
            if event.button() == Qt.LeftButton and self.current_building_type is not None:
                offset = self.calculate_rotated_offset(self.ghost_item)
                self._place_building(self.last_mouse_scene_pos - offset)

            elif event.button() == Qt.RightButton and self.current_building_type is not None:
                self.current_building_type = None
                if self.ghost_item:
                    self.removeItem(self.ghost_item)
                self.ghost_item = None
                self.operation = None
        
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.last_mouse_scene_pos = event.scenePos()
        self.snap_preview_to_cursor()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_current_selection()
        elif event.key() == Qt.Key.Key_A and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.select_all_items()
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.copy_current_selection()
        elif event.key() == Qt.Key.Key_X and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.cut_current_selection()
        elif event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.paste_current_selection()
        elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.save_layout_to_file()
        elif event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.load_layout_from_file()
        elif self.operation == SceneOperation.BUILDING_PLACEMENT and event.key() == Qt.Key.Key_R:
            self.rotate_preview()
        else:
            super().keyPressEvent(event)
