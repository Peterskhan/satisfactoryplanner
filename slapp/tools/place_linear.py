from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QColor
from PySide6.QtWidgets import QGraphicsColorizeEffect

from slapp.editor.settings import Settings
from slapp.tools.tool_base import EditorTool, EditorContext
from slapp.items.linear import LinearItem
from slapp.core.linear import *


class LinearPlacementTool(EditorTool):
    """
    Handles placement of linear layout elements, eg. Conveyor lines.

    Mouse movement: Control node preview follows the mouse and snaps to grid.
    Left click: Place a control node at the current mouse position.
    Right click: Interrupt the placement process.
    """
    context: EditorContext
    preview_item: LinearItem

    def __init__(self, context: EditorContext, type: 'LineType'):
        self.context = context
        self.preview_item = LinearItem(LinearElement(type))
        self.preview_item.instance.add_preview_node()
        self.preview_item.update_from_instance()
        self.preview_item.setOpacity(0.4)
        self.preview_item.setZValue(9999)
        self.context.add_preview_item(self.preview_item)

        self.snap_preview_to_cursor()
        self.preview_item.update_from_instance()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if self.preview_item is None:
            return

        if event.button() == Qt.LeftButton:
            self.preview_item.instance.accept_preview_node()
            self.preview_item.instance.add_preview_node()
            self.snap_preview_to_cursor()
            self.preview_item.update_from_instance()

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

    def cancel(self) -> None:
        """Cancels the placement."""
        instance = self.preview_item.instance.clone()
        self.context.add_item(LinearItem(instance))
        self.context.remove_preview_item(self.preview_item)
        self.preview_item = None
        self.context.exit_tool()

    def rotate(self) -> None:
        """Rotations are not handled."""
        pass

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
        self.preview_item.instance.move_preview_node_to(Position(round(snapped_x / scale),
                                                                 round(snapped_y / scale)))