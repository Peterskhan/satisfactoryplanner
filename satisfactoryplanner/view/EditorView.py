from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QPixmap, QTransform, QGuiApplication
from PySide6.QtCore import Qt, QRectF
from view.Settings import Settings
from view.EditorScene import EditorScene

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

        # Panning
        self._isPanning = False
        self._panStart = None

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

    # --- Grid Drawing ---
    GRID_SIZE = Settings.PIXELS_PER_METER
    GRID_SUBDIV = 8

    def drawBackground(self, painter, rect: QRectF):
        super().drawBackground(painter, rect)

        scene_rect = self.scene().sceneRect().adjusted(8 * self.GRID_SIZE, 8 * self.GRID_SIZE, - 8 * self.GRID_SIZE, -8 * self.GRID_SIZE)

        # --- Grid restricted to scene ---
        left = int(scene_rect.left())
        right = int(scene_rect.right())
        top = int(scene_rect.top())
        bottom = int(scene_rect.bottom())

        minor_pen = QPen(QColor(60, 60, 60))
        minor_pen.setWidth(2)
        major_pen = QPen(QColor(90, 90, 90))
        major_pen.setWidth(5)

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
        border_pen.setWidth(10)
        painter.setPen(border_pen)
        painter.drawRect(scene_rect)

        # --- Optional: origin marker ---
        origin_pen = QPen(QColor(255, 255, 255))
        origin_pen.setWidth(2)
        painter.setPen(origin_pen)
        painter.drawLine(-10, -10, 10, 10)
        painter.drawLine(-10, 10, 10, -10)

        #pix = QPixmap("./resources/StorageContainer.png")
        #pen = QPen()
        #pen.setWidth(10)
        #brush = QBrush(pix)
        #scale = pen.width() / pix.height()
        #transform = QTransform()
        #transform.scale(scale, scale)
        #brush.setTransform(transform)
        #pen.setBrush(brush)
        #painter.setPen(pen)
        #painter.drawLine(0, 0, 200, 0)
        #painter.drawLine(200, 0, 200, 200)
