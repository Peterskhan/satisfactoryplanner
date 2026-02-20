from PySide6.QtWidgets import QGraphicsScene, QFileDialog, QGraphicsColorizeEffect
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor
from view.Settings import Settings
from view.BuildingItem import BuildingItem
from model.BuldingInstance import BuildingInstance, BuildingType, Position, Rotation
from model.FactoryLayout import FactoryLayout, type_lookup
from enum import Enum

class SceneOperation(Enum):
    BUILDING_PLACEMENT = 1
    BUILDING_REMOVAL = 2

class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    layout: FactoryLayout
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
        self.clipboard_layout = None

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

    def delete_current_selection(self):
        for item in self.selectedItems():
            self.layout.remove_building(item.instance)
            self.removeItem(item)

    def select_all_items(self):
        for item in self.items():
            item.setSelected(True)

    def copy_current_selection(self):
        self.clipboard_layout = FactoryLayout.create_from_buildings([item.instance for item in self.selectedItems()])
        
    def cut_current_selection(self):
        self.clipboard_layout = FactoryLayout.create_from_buildings([item.instance for item in self.selectedItems()])
        self.delete_current_selection()

    def paste_current_selection(self):
        if self.clipboard_layout:
            layout_to_paste = self.clipboard_layout.clone()
            self.layout.add_sublayout(layout_to_paste, offset_x=4, offset_y=4)
            items_to_paste = [BuildingItem(instance) for instance in layout_to_paste.buildings]

            self.clearSelection()
            for item in items_to_paste:
                item.setSelected(True)
                item.update()
                self.addItem(item)

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
        instance = self.preview_item.instance.clone()
        self.layout.add_building(instance)
        self.addItem(BuildingItem(instance))

    def set_preview(self, building_type: BuildingType):
        if self.preview_item:
            self.removeItem(self.preview_item)

        self.preview_item = BuildingItem(BuildingInstance(building_type, Position(0, 0), Rotation.DEG_0))
        self.preview_item.setOpacity(0.4)
        self.preview_item.setZValue(9999)  # always on top

        self.addItem(self.preview_item)

    def rotate_preview(self):
        self.preview_item.instance.rotate_clockwise()
        self.preview_item.update()

    def snap_preview_to_cursor(self):
        if self.preview_item:
            snapped_x = round(self.last_mouse_scene_pos.x() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            snapped_y = round(self.last_mouse_scene_pos.y() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            self.preview_item.setPos(snapped_x, snapped_y)

            self.preview_item.instance.move_to(round(snapped_x / Settings.PIXELS_PER_METER),
                                               round(snapped_y / Settings.PIXELS_PER_METER))

    def check_collisions(self):
        if self.preview_item:
            colliding = self.preview_item.is_colliding()
            effect = QGraphicsColorizeEffect()
            effect.setColor(QColor('red'))
            effect.setStrength(0.5)

            self.preview_item.setGraphicsEffect(effect if colliding else None)

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
            self.check_collisions()
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
