from PySide6.QtGui import QMouseEvent, QKeyEvent

class PlacementTool:
    """Abstract interface for Editor placement tools."""

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release events."""

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events."""
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
