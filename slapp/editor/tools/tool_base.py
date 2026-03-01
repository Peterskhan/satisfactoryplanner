from PySide6.QtCore import QObject, QPointF
from PySide6.QtGui import QMouseEvent, QKeyEvent

class EditorContext:
    """Context for tools to access the scene in a controlled way."""

    def __init__(self, scene: 'EditorScene') -> None:
        """Initialize the EditorContext."""
        self.scene = scene
        self.last_mouse_scene_pos = QPointF(0, 0)

    def exit_tool(self):
        """Instruct the scene to exit the current tool."""
        self.scene.set_tool(None, should_cancel=False)

    def add_item(self, item) -> None:
        """Add an item to the scene."""
        self.scene.addItem(item)

    def remove_item(self, item) -> None:
        """Remove an item from the scene."""
        self.scene.removeItem(item)

    def layout(self):
        """Get the FactoryLayout of the scene."""
        return self.scene.layout

    def last_mouse_scene_position(self) -> QPointF:
        """Get the last known scene position of the mouse."""
        return self.last_mouse_scene_pos

    def set_lat_mouse_scene_position(self, position: QPointF) -> None:
        """Set the last known scene position of the mouse."""
        self.last_mouse_scene_pos = position

class EditorTool(QObject):
    """Abstract interface for Editor placement tools."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events."""

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events."""

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""

    def rotate(self) -> None:
        """Handle rotation requests."""

    def cancel(self) -> None:
        """Handle cancel requests."""
