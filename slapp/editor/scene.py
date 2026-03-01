from PySide6.QtWidgets import QGraphicsScene, QFileDialog
from PySide6.QtCore import QPointF, Signal
from slapp.editor.tools.tool_base import EditorTool, EditorContext
from slapp.editor.tools.place_discrete import DiscretePlacementTool
from slapp.editor.tools.place_linear import LinearPlacementTool
from slapp.editor.tools.measure import MeasurementTool
from slapp.editor.items.discrete import DiscreteItem
from slapp.editor.items.linear import LinearItem
from slapp.core.factory import FactoryLayout
from slapp.core.discrete import BuildingType, Position
from slapp.core.linear import LineType, line_types
from slapp.editor.settings import Settings


class EditorScene(QGraphicsScene):
    """The graphical representation of the factory editor's world."""

    layout: FactoryLayout

    def __init__(self, parent, layout: FactoryLayout):
        super().__init__(parent)
        self.setSceneRect(-10000, -10000, 20000, 20000)
        self.layout = layout
        self.save_file_path = None
        self.clipboard_layout = None
        self.tool = None
        self.context = EditorContext(self)

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
            self.set_tool(DiscretePlacementTool(self.context, type))
        elif isinstance(type, LineType):
            self.set_tool(LinearPlacementTool(self.context, type))

        # Hack to ensure the scene has focus for key events (e.g. rotation)
        # immediately after selecting a building type
        self.views()[0].setFocus()

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
        if self.tool:
            self.set_tool(None)

    ## ======================================================
    ## Helper methods
    ## ======================================================

    def set_tool(self, tool: EditorTool, should_cancel: bool = True) -> None:
        if self.tool and should_cancel:
            self.tool.cancel()

        self.tool = tool

    def scene_to_world(self, scene_pos: QPointF) -> Position:
        return Position(scene_pos.x() / Settings.PIXELS_PER_METER,
                        scene_pos.y() / Settings.PIXELS_PER_METER)

    def scene_to_world_snapped(self, scene_pos: QPointF) -> Position:
        x = round(scene_pos.x() / Settings.PIXELS_PER_METER)
        y = round(scene_pos.y() / Settings.PIXELS_PER_METER)
        return Position(x, y)

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
        self.mouse_scene_position_changed.emit(f'Scene Position: ({scene_pos.x():.2f}, {scene_pos.y():.2f}) '
                                               f'World Position: ({world_pos.x:.2f}, {world_pos.y:.2f}) '
                                               f'Snapped World Position: ({snapped_world_pos.x}, {snapped_world_pos.y})')
        self.context.set_lat_mouse_scene_position(event.scenePos())
        super().mouseMoveEvent(event)
