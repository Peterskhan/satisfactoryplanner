from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QColor
from PySide6.QtWidgets import QGraphicsColorizeEffect
from slapp.tools.tool_base import EditorTool, EditorContext
from slapp.items.discrete import DiscreteItem
from slapp.editor.settings import Settings
from slapp.core.discrete import *


class DiscretePlacementTool(EditorTool):
    """
    Handles placement of discrete layout elements, eg. Buildings.

    Mouse movement: Items follow the cursor and snap to grid.
    Left click: Place a clone of the current preview.
    Right click: Interrupt the placement process.
    """
    context: EditorContext
    preview_item: DiscreteItem

    def __init__(self, context: EditorContext, type: 'BuildingType'):
        self.context = context
        self.preview_item = DiscreteItem(DiscreteElement(type, Position(0, 0), Rotation.DEG_0))
        self.preview_item.setOpacity(0.4)
        self.preview_item.setZValue(9999)
        self.context.add_preview_item(self.preview_item)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if self.preview_item is None:
            return

        if event.button() == Qt.LeftButton:
            instance = self.preview_item.instance.clone()
            self.context.add_item(DiscreteItem(instance))

        elif event.button() == Qt.RightButton:
            self.cancel()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events."""
        if self.preview_item is None:
            return

        self.snap_preview_to_cursor()
        self.check_collisions()
        self.preview_item.update_from_instance()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if self.preview_item is None:
            return

    def rotate(self) -> None:
        if self.preview_item:
            self.preview_item.instance.rotate_clockwise()
            self.preview_item.update_from_instance()

    def cancel(self) -> None:
        self.context.remove_preview_item(self.preview_item)
        self.preview_item = None
        self.context.exit_tool()

    def check_collisions(self):
        if self.preview_item:
            colliding = self.preview_item.is_colliding()
            effect = QGraphicsColorizeEffect()
            effect.setColor(QColor('red'))
            effect.setStrength(0.5 if colliding else 0.0)
            self.preview_item.setGraphicsEffect(effect)

    def snap_preview_to_cursor(self):
        scale = Settings.PIXELS_PER_METER
        snapped_x = round(self.context.last_mouse_scene_position().x() / scale) * scale
        snapped_y = round(self.context.last_mouse_scene_position().y() / scale) * scale
        self.preview_item.setPos(snapped_x, snapped_y)
        self.preview_item.instance.move_to(round(snapped_x / scale),
                                           round(snapped_y / scale))
