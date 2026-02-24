from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent

from slapp.view.editor.tools.placement_tool import PlacementTool
from slapp.view.editor.EditorScene import EditorScene


class DiscretePlacementTool(PlacementTool):
    """
    Handles placement of discrete layout elements, eg. Buildings.

    Mouse movement: Items follow the cursor and snap to grid.
    Left click: Place a clone of the current preview.
    Right click: Interrupt the placement process.
    """

    def __init__(self, scene: EditorScene):
        self.scene = scene
        self.preview_item = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press events."""
        if self.preview_item is None:
            return 
        
        if event.button() == Qt.LeftButton:
            pass
        
        elif event.button() == Qt.RightButton:
            pass

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse move events."""
        if self.preview_item is None:
            return
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle key press events."""
        if self.preview_item is None:
            return