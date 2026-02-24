from PySide6.QtWidgets import QGraphicsScene, QFileDialog, QGraphicsColorizeEffect
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QColor
from slapp.view.editor.Settings import Settings
from slapp.core.DiscreteElement import DiscreteElement, BuildingType, Position, Rotation
from slapp.view.items.DiscreteItem import DiscreteItem
from slapp.core.LinearElement import LineType, LinearElement, line_types
from slapp.view.items.LinearItem import LinearItem
from slapp.core.FactoryLayout import FactoryLayout
from enum import Enum

class SceneOperation(Enum):
    BUILDING_PLACEMENT = 1
    LINE_PLACEMENT = 2
    BUILDING_REMOVAL = 3

class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    layout: FactoryLayout
    operation: SceneOperation
    preview_item: DiscreteItem | LinearItem

    def __init__(self, parent, layout: FactoryLayout):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.preview_item = None
        self.layout = layout
        self.save_file_path = None
        self.operation = None
        self.last_mouse_scene_pos = None
        self.clipboard_layout = None

    ## ======================================================
    ## Signals
    ## ======================================================

    mouse_scene_position_changed = Signal(str)

    loaded_file_changed = Signal(str)

    ## ======================================================
    ## Slots
    ## ======================================================

    def set_preview_type(self, type: BuildingType | LineType):
        if isinstance(type, BuildingType):
            self.operation = SceneOperation.BUILDING_PLACEMENT
        elif isinstance(type, LineType):
            self.operation = SceneOperation.LINE_PLACEMENT
        else:
            raise ValueError(f'Invalid type for preview: {type}')

        # Hack to ensure the scene has focus for key events (e.g. rotation)
        # immediately after selecting a building type
        self.views()[0].setFocus()
        self.set_preview(type)

    def delete_current_selection(self):
        for item in self.selectedItems():
            self.layout.remove_instance(item.instance)
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
            items_to_paste = [DiscreteItem(instance) for instance in layout_to_paste.buildings]

            self.clearSelection()
            for item in items_to_paste:
                item.setSelected(True)
                item.update_from_instance()
                self.addItem(item)

    def rotate_current_selection(self):
        for item in self.selectedItems():
            if isinstance(item, DiscreteItem):
                item.instance.rotate_clockwise()
                item.update_from_instance()

    def new_layout(self):
        self.layout.clear()

        for item in self.items():
            self.removeItem(item)

        self.save_file_path = None
        self.loaded_file_changed.emit(self.save_file_path)

    def save_layout_to_file(self):
        if not self.save_file_path:
            self.save_layout_to_file_as()
        else:
            with open(self.save_file_path, mode='w') as save_file:
                save_file.write(self.layout.serialize())

    def save_layout_to_file_as(self):
        save_file_path, _ = QFileDialog.getSaveFileName(
            None,
            'Save file',
            'factory.fl',
            'Factory layouts (*.fl)'
        )

        if not save_file_path:
            return

        with open(save_file_path, mode='w') as save_file:
            save_file.write(self.layout.serialize())

        self.save_file_path = save_file_path
        self.loaded_file_changed.emit(self.save_file_path)

    def load_layout_from_file(self):
        open_file_path, _ = QFileDialog.getOpenFileName(
            None,
            'Open file',
            '',
            'Factory layouts (*.fl)'
        )

        if not open_file_path:
            return

        # Clear existing items
        for item in self.items():
            self.removeItem(item)

        with open(open_file_path, mode='r') as load_file:
            json_str = load_file.read()
            self.layout.deserialize(json_str)

            for building in self.layout.buildings:
                self.addItem(DiscreteItem(building))

            for line in self.layout.lines:
                self.addItem(LinearItem(line))

        self.save_file_path = open_file_path
        self.loaded_file_changed.emit(self.save_file_path)

    def cancel_current_operation(self):
        if self.operation is not None:
            self.operation = None

        if self.preview_item is not None:
            self.removeItem(self.preview_item)
            self.preview_item = None

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
        self.layout.add_instance(instance)
        self.addItem(DiscreteItem(instance))

    def place_line(self):
        instance = self.preview_item.instance.clone()
        self.layout.add_line(instance)
        item = LinearItem(instance)
        item.setSelected(True)
        self.addItem(item)

    def build_conveyor(self):
        if self.operation == None:
            self.set_preview_type(line_types['Conveyor belt'])

    def rotate_current(self):
        if self.operation == SceneOperation.BUILDING_PLACEMENT:
            self.rotate_preview()
        else:
            self.rotate_current_selection()

    def rotate_preview(self):
        self.preview_item.instance.rotate_clockwise()
        self.preview_item.update_from_instance()

    def set_preview(self, type: BuildingType | LineType):
        if self.preview_item:
            self.removeItem(self.preview_item)

        if isinstance(type, BuildingType):
            self.preview_item = DiscreteItem(DiscreteElement(type, Position(0, 0), Rotation.DEG_0))
        elif isinstance(type, LineType):
            self.preview_item = LinearItem(LinearElement(type))
            self.preview_item.instance.add_preview_node()
            self.snap_preview_to_cursor()
            self.preview_item.update_from_instance()
        else:
            raise ValueError('Invalid type for preview')

        self.preview_item.setOpacity(0.4)
        self.preview_item.setZValue(9999)
        self.addItem(self.preview_item)

    def snap_preview_to_cursor(self):
        if self.preview_item:
            snapped_x = round(self.last_mouse_scene_pos.x() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            snapped_y = round(self.last_mouse_scene_pos.y() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER

            if isinstance(self.preview_item.instance, DiscreteElement):
                self.preview_item.setPos(snapped_x, snapped_y)
                self.preview_item.instance.move_to(round(snapped_x / Settings.PIXELS_PER_METER),
                                                   round(snapped_y / Settings.PIXELS_PER_METER))
            elif isinstance(self.preview_item.instance, LinearElement):
                self.preview_item.instance.move_preview_node_to(Position(round(snapped_x / Settings.PIXELS_PER_METER),
                                                                         round(snapped_y / Settings.PIXELS_PER_METER)))
            else:
                raise ValueError('Invalid preview item type')

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
        if event.button() == Qt.LeftButton and self.preview_item:
            if self.operation == SceneOperation.BUILDING_PLACEMENT:
                self.place_building()
            elif self.operation == SceneOperation.LINE_PLACEMENT:
                self.preview_item.instance.accept_preview_node()
                self.preview_item.instance.add_preview_node()
                self.snap_preview_to_cursor()
                self.preview_item.update_from_instance()
                super().mousePressEvent(event)

        elif event.button() == Qt.RightButton and self.preview_item:
            if self.operation == SceneOperation.BUILDING_PLACEMENT:
                if self.preview_item:
                    self.removeItem(self.preview_item)
            elif self.operation == SceneOperation.LINE_PLACEMENT:
                if self.preview_item:
                    self.removeItem(self.preview_item)
                    self.place_line()

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
            self.preview_item.update_from_instance()
        super().mouseMoveEvent(event)
