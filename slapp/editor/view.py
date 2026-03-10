from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QColor, QPainter, QPen, QGuiApplication
from PySide6.QtCore import Qt, QRectF
from slapp.editor.settings import Settings
from slapp.editor.scene import EditorScene

class EditorView(QGraphicsView):
    def __init__(self, scene: EditorScene):
        super().__init__()
        self.setScene(scene)

        self.setBackgroundBrush(QColor("#202020"))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Zoom behavior
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self._zoom = 0
        self._zoom_range = (-12, 5)
        self.scale(0.2, 0.2)

        # Panning
        self._isPanning = False
        self._panStart = None

        self.setBackgroundBrush(Qt.NoBrush)

    # --- Mouse Panning ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            QGuiApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self._isPanning = True
            self._panStart = event.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            QGuiApplication.restoreOverrideCursor()
            self._isPanning = False
            self._panStart = None
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._isPanning:
            delta = event.pos() - self._panStart
            self._panStart = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        else:
            super().mouseMoveEvent(event)

    # --- Zoom ---
    def wheelEvent(self, event):
        zoom_factor = 1.25
        old_pos = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            if self._zoom >= self._zoom_range[1]:
                return
            self._zoom += 1
            self.scale(zoom_factor, zoom_factor)
        else:
            if self._zoom <= self._zoom_range[0]:
                return
            self._zoom -= 1
            self.scale(1 / zoom_factor, 1 / zoom_factor)

        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
        self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
