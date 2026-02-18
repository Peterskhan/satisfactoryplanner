from PySide6.QtWidgets import QGraphicsScene, QFileDialog
from PySide6.QtCore import Qt, QPointF, Signal
from view.Settings import Settings
from view.BuildingItem import BuildingItem
from model.building import BuildingType
from model.FactoryLayout import FactoryLayout, Position, Rotation, type_lookup
from enum import Enum

class SceneOperation(Enum):
    BUILDING_PLACEMENT = 1
    BUILDING_REMOVAL = 2

class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    operation: SceneOperation
    preview_item: BuildingItem

    def __init__(self, parent, layout: FactoryLayout):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.preview_item = None
        self.layout = layout
        self.save_file = None
        self.operation = None
        self.last_mouse_scene_pos = None

    ## ======================================================
    ## Signals
    ## ====================================================== 

    mouse_scene_position_changed = Signal(str)

    ## ======================================================
    ## Slots
    ## ====================================================== 

    def set_preview_type(self, building_type: BuildingType):
        self.operation = SceneOperation.BUILDING_PLACEMENT

        # This is a hack, because the view does not have focus to handle rotation events
        self.views()[0].setFocus()
        self.set_preview(building_type)

    ## ======================================================
    ## Helper methods
    ## ======================================================

    def scene_to_world(self, scene_pos: QPointF) -> Position:
        return Position(scene_pos.x() / Settings.PIXELS_PER_METER, 
                        scene_pos.y() / Settings.PIXELS_PER_METER)
    
    def scene_to_world_snapped(self, scene_pos: QPointF) -> Position:
        x = round(scene_pos.x() / Settings.PIXELS_PER_METER)
        y = round(scene_pos.y() / Settings.PIXELS_PER_METER)
        return Position(x, y)

    def place_building(self):
        instance = self.layout.add_building(
            self.preview_item.instance.type,
            self.preview_item.instance.position,
            self.preview_item.instance.rotation
        )
        self.addItem(BuildingItem(instance))

    def set_preview(self, building_type: BuildingType):
        if self.preview_item:
            self.removeItem(self.preview_item)

        self.preview_item = BuildingItem(self.layout.create_building(building_type, Position(0, 0), Rotation.DEG_0))
        self.preview_item.setOpacity(0.4)
        self.preview_item.setZValue(9999)  # always on top

        self.addItem(self.preview_item)

    def rotate_preview(self):
        self.preview_item.instance.rotate_clockwise()
        self.snap_preview_to_cursor()
        self.preview_item.update()

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
        if self.preview_item is not None:
            offset = self.calculate_rotated_offset(self.preview_item)
            snapped = self.scene_to_world_snapped(self.last_mouse_scene_pos - offset)
            self.preview_item.instance.move_to(snapped.x, snapped.y)

    def delete_current_selection(self):
        for item in self.selectedItems():
            self.layout.remove_building(item.instance)
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

    def rotate_current_selection(self):
        for item in self.selectedItems():
            if isinstance(item, BuildingItem):
                item.instance.rotate_clockwise()
                item.update()

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
            save_file.write(self.layout.serialize())

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
            self.layout.deserialize(json_str, type_lookup)

        # Clear existing items
        for item in self.items():
            self.removeItem(item)

        # Add items from the loaded layout
        for building in self.layout.buildings:
            self.addItem(BuildingItem(building))

    ## ======================================================
    ## Event handlers
    ## ======================================================

    def mousePressEvent(self, event):
        if self.operation == SceneOperation.BUILDING_PLACEMENT:
            if event.button() == Qt.LeftButton and self.preview_item:
                self.place_building()

            elif event.button() == Qt.RightButton and self.preview_item:
                if self.preview_item:
                    self.removeItem(self.preview_item)
                self.preview_item = None
                self.operation = None
        
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        scene_pos = event.scenePos()
        world_pos = self.scene_to_world(scene_pos)
        snapped_world_pos = self.scene_to_world_snapped(scene_pos)
        self.mouse_scene_position_changed.emit(f'Scene Position: ({scene_pos.x():.2f}, {scene_pos.y():.2f}) '
                                               f'World Position: ({world_pos.x:.2f}, {world_pos.y:.2f}) '
                                               f'Snapped World Position: ({snapped_world_pos.x}, {snapped_world_pos.y})')
        self.last_mouse_scene_pos = event.scenePos()
        if self.preview_item:
            self.snap_preview_to_cursor()
            self.preview_item.update()
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
        elif event.key() == Qt.Key.Key_R:
            if self.operation == SceneOperation.BUILDING_PLACEMENT:
                self.rotate_preview()
            else:
                self.rotate_current_selection()
        else:
            super().keyPressEvent(event)
