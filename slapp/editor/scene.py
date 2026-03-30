from PySide6.QtWidgets import QGraphicsScene, QFileDialog
from PySide6.QtGui import QPen, QColor
from PySide6.QtCore import QRectF
from PySide6.QtCore import QPointF, Signal
from slapp.tools.tool_base import EditorTool, EditorContext
from slapp.tools.place_discrete import DiscretePlacementTool
from slapp.tools.place_linear import LinearPlacementTool
from slapp.tools.measure import MeasurementTool
from slapp.items.discrete import DiscreteItem
from slapp.items.linear import LinearItem
from slapp.core.factory import Factory
from slapp.core.layout import Layout
from slapp.core.floor import Floor
from slapp.core.discrete import BuildingType
from slapp.core.linear import LineType, line_types
from slapp.editor.settings import Settings

from collections import defaultdict
import json

class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    factory: Factory
    _current_floor: Floor
    _floor_to_items: dict[Floor, list[DiscreteItem | LinearItem]]
    _preview_items: list[DiscreteItem | LinearItem]

    def __init__(self, parent):
        super().__init__(parent)

        self.save_file_path = None
        self.clipboard_layout = None
        self.tool = None
        self.context = EditorContext(self)
        self._is_grid_visible = True

        self.initialize_layout()

    ## ======================================================
    ## Signals
    ## ======================================================

    def add_item(self, item: DiscreteItem | LinearItem, add_to_layout: bool = True):
        if add_to_layout:
            self._current_floor.layout.add_element(item.instance)
        self._floor_to_items[self._current_floor].append(item)
        self.addItem(item)
        item.setVisible(True)

    def add_preview_item(self, item: DiscreteItem | LinearItem):
        self._preview_items.append(item)
        self.addItem(item)

    def remove_item(self, item: DiscreteItem | LinearItem):
        self._current_floor.layout.remove_element(item.instance)
        self._floor_to_items[self._current_floor].remove(item)
        self.removeItem(item)

    def remove_preview_item(self, item: DiscreteItem | LinearItem):
        self._preview_items.remove(item)
        self.removeItem(item)

    mouse_scene_position_changed = Signal(str)
    loaded_file_changed = Signal(str)
    factory_changed = Signal()

    ## ======================================================
    ## Slots
    ## ======================================================

    def change_floor(self, desired_floor: Floor) -> None:
        for floor, items_on_floor in self._floor_to_items.items():
            visible = (floor == desired_floor)
            for item in items_on_floor:
                item.setVisible(visible)
        self._current_floor = desired_floor

    def set_preview_type(self, type: BuildingType | LineType):
        if isinstance(type, BuildingType):
            self.set_tool(DiscretePlacementTool(self.context, type))
        elif isinstance(type, LineType):
            self.set_tool(LinearPlacementTool(self.context, type))

        # Hack to ensure the scene has focus for key events (e.g. rotation)
        # immediately after selecting a building type
        self.views()[0].setFocus()

    def delete_current_selection(self):
        for item in self.selectedItems():
            self._current_floor.layout.remove_element(item.instance)
            self._floor_to_items[self._current_floor].remove(item)
            self.removeItem(item)

    def select_all_items(self):
        for item in self._floor_to_items[self._current_floor]:
            item.setSelected(True)

    def copy_current_selection(self):
        self.clipboard_layout = Layout.from_buildings([item.instance for item in self.selectedItems()])

    def cut_current_selection(self):
        self.clipboard_layout = Layout.from_buildings([item.instance for item in self.selectedItems()])
        self.delete_current_selection()

    def paste_current_selection(self):
        if self.clipboard_layout:
            layout_to_paste = self.clipboard_layout.clone()
            self._current_floor.layout.add_sublayout(layout_to_paste, offset=QPointF(4, 4))
            items_to_paste = [DiscreteItem(instance) for instance in layout_to_paste.buildings]

            self.clearSelection()
            for item in items_to_paste:
                self.add_item(item, add_to_layout=False)
                item.setSelected(True)

    def rotate_current_selection(self):
        for item in self.selectedItems():
            if isinstance(item, DiscreteItem):
                item.instance.rotate(90)

    def initialize_layout(self):

        for item in self.items():
            self.removeItem(item)

        if self.tool:
            self.set_tool(None)

        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.factory = Factory()
        self._current_floor = self.factory.floors[0]
        self._floor_to_items = defaultdict(list)
        self._preview_items = []
        self.factory_changed.emit()

        self.save_file_path = None
        self.clipboard_layout = None
        self.context = EditorContext(self)
        self.loaded_file_changed.emit(self.save_file_path)
        self.change_floor(self._current_floor)

    def active_floor(self) -> Floor:
        return self._current_floor

    def save_layout_to_file(self):
        if not self.save_file_path:
            self.save_layout_to_file_as()
        else:
            with open(self.save_file_path, mode='w') as save_file:
                save_file.write(json.dumps(self.factory.serialize(), indent=2))

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
            save_file.write(json.dumps(self.factory.serialize()))

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

        self.initialize_layout()

        with open(open_file_path, mode='r') as load_file:
            json_str = load_file.read()
            factory_data = json.loads(json_str)
            self.factory = Factory.deserialize(factory_data)
            self._current_floor = self.factory.floors[0]
            self.factory_changed.emit()

            for floor in self.factory.floors:
                self.change_floor(floor)
                for discrete_element in floor.layout.buildings:
                    self.add_item(DiscreteItem(discrete_element), add_to_layout=False)
                for linear_element in floor.layout.lines:
                    self.add_item(LinearItem(linear_element), add_to_layout=False)

        self._current_floor = self.factory.floors[0]
        self.change_floor(self._current_floor)

        self.save_file_path = open_file_path
        self.loaded_file_changed.emit(self.save_file_path)

    def cancel_current_operation(self):
        if self.tool:
            self.set_tool(None)

    ## ======================================================
    ## Helper methods
    ## ======================================================

    def set_tool(self, tool: EditorTool, should_cancel: bool = True) -> None:
        if self.tool and should_cancel:
            self.tool.cancel()

        self.tool = tool

    @staticmethod
    def scene_to_world(scene_pos: QPointF) -> QPointF:
        return scene_pos / Settings.PIXELS_PER_METER

    @staticmethod
    def scene_to_world_snapped(scene_pos: QPointF) -> QPointF:
        x = round(scene_pos.x() / Settings.PIXELS_PER_METER)
        y = round(scene_pos.y() / Settings.PIXELS_PER_METER)
        return QPointF(x, y)

    def build_conveyor(self):
        self.set_preview_type(line_types['Conveyor belt'])

    def start_measurement(self):
        self.set_tool(MeasurementTool(self.context))

    def rotate_current(self):
        if self.tool:
            self.tool.rotate()
        else:
            self.rotate_current_selection()

    ## ======================================================
    ## Event handlers
    ## ======================================================

    def mousePressEvent(self, event):
        if self.tool:
            self.tool.mousePressEvent(event)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.tool:
            self.tool.mouseMoveEvent(event)

        scene_pos = event.scenePos()
        world_pos = self.scene_to_world(scene_pos)
        snapped_world_pos = self.scene_to_world_snapped(scene_pos)
        self.mouse_scene_position_changed.emit(f'Scene: ({scene_pos.x():.2f}, {scene_pos.y():.2f}) '
                                               f'World: ({world_pos.x():.2f}, {world_pos.y():.2f}) '
                                               f'Snapped: ({snapped_world_pos.x()}, {snapped_world_pos.y()})')
        self.context.set_mouse_scene_position(event.scenePos())
        super().mouseMoveEvent(event)

    def set_grid_visible(self, visible: bool) -> None:
        self._is_grid_visible = visible
        self.update()

    def drawBackground(self, painter, rect: QRectF):
        super().drawBackground(painter, rect)

        if not self._is_grid_visible:
            return

        self.GRID_SIZE = Settings.PIXELS_PER_METER
        self.GRID_SUBDIV = 8

        scene_rect = self.sceneRect().adjusted(8 * self.GRID_SIZE, 8 * self.GRID_SIZE, - 8 * self.GRID_SIZE, -8 * self.GRID_SIZE)

        # --- Grid restricted to scene ---
        left = int(scene_rect.left())
        right = int(scene_rect.right())
        top = int(scene_rect.top())
        bottom = int(scene_rect.bottom())

        minor_pen = QPen(QColor(60, 60, 60))
        minor_pen.setWidthF(0.5)
        minor_pen.setCosmetic(True)
        major_pen = QPen(QColor(90, 90, 90))
        major_pen.setWidthF(1.5)
        major_pen.setCosmetic(True)

        lines_minor = []
        lines_major = []

        # Vertical lines
        x = left - (left % self.GRID_SIZE)
        while x <= right:
            if (x // self.GRID_SIZE) % self.GRID_SUBDIV == 0:
                lines_major.append((x, top, x, bottom))
            else:
                lines_minor.append((x, top, x, bottom))
            x += self.GRID_SIZE

        # Horizontal lines
        y = top - (top % self.GRID_SIZE)
        while y <= bottom:
            if (y // self.GRID_SIZE) % self.GRID_SUBDIV == 0:
                lines_major.append((left, y, right, y))
            else:
                lines_minor.append((left, y, right, y))
            y += self.GRID_SIZE

        # Draw grid
        painter.setPen(minor_pen)
        for x1, y1, x2, y2 in lines_minor:
            painter.drawLine(x1, y1, x2, y2)

        painter.setPen(major_pen)
        for x1, y1, x2, y2 in lines_major:
            painter.drawLine(x1, y1, x2, y2)

        # --- Thick border around usable area ---
        border_pen = QPen(QColor('lightgray'))
        border_pen.setWidth(2.5)
        border_pen.setCosmetic(True)
        painter.setPen(border_pen)
        painter.drawRect(scene_rect)

        # --- Optional: origin marker ---
        origin_pen = QPen(QColor(255, 255, 255))
        origin_pen.setWidth(2)
        painter.setPen(origin_pen)
        painter.drawLine(-10, -10, 10, 10)
        painter.drawLine(-10, 10, 10, -10)
