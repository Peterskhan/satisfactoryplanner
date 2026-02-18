from PySide6.QtWidgets import QGraphicsView
from PySide6.QtGui import QColor, QPainter, QPen, QTransform
from PySide6.QtCore import Qt, QRectF

from view.Settings import Settings
from view.EditorScene import EditorScene
from model.FactoryLayout import FactoryLayout

class EditorView(QGraphicsView):
    def __init__(self, layout: FactoryLayout):
        super().__init__()

        scene = EditorScene(self, layout)
        self.setScene(scene)

        self.setBackgroundBrush(QColor("#202020"))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 🔑 THIS is what you want
        # self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Zoom behavior
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self._zoom = 0
        self._zoom_range = (-100, 200)
        self._isPanning = False
        self._panStart = None

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):
            self._isPanning = True
            self._panStart = event.pos()
            return

        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MouseButton.MiddleButton):
            self._isPanning = False
            self._panStart = None
            return

        return super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if (self._isPanning):
            delta = event.pos() - self._panStart
            self._panStart = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            return

        return super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        zoom_factor = 1.25

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

    GRID_SIZE = Settings.PIXELS_PER_METER
    GRID_SUBDIV = 8  # major line every 8 cells

    def drawBackground(self, painter, rect: QRectF):
        super().drawBackground(painter, rect)

        left = int(rect.left()) - (int(rect.left()) % self.GRID_SIZE)
        top = int(rect.top()) - (int(rect.top()) % self.GRID_SIZE)

        minor_pen = QPen(QColor(60, 60, 60))
        minor_pen.setWidth(2)
        major_pen = QPen(QColor(90, 90, 90))
        major_pen.setWidth(5)

        origin_pen = QPen(QColor(255, 255, 255))
        origin_pen.setWidth(2)

        lines_minor = []
        lines_major = []

        x = left
        while x < rect.right():
            if (x // self.GRID_SIZE) % self.GRID_SUBDIV == 0:
                lines_major.append((x, rect.top(), x, rect.bottom()))
            else:
                lines_minor.append((x, rect.top(), x, rect.bottom()))
            x += self.GRID_SIZE

        y = top
        while y < rect.bottom():
            if (y // self.GRID_SIZE) % self.GRID_SUBDIV == 0:
                lines_major.append((rect.left(), y, rect.right(), y))
            else:
                lines_minor.append((rect.left(), y, rect.right(), y))
            y += self.GRID_SIZE

        painter.setPen(minor_pen)
        for x1, y1, x2, y2 in lines_minor:
            painter.drawLine(x1, y1, x2, y2)

        painter.setPen(major_pen)
        for x1, y1, x2, y2 in lines_major:
            painter.drawLine(x1, y1, x2, y2)

        painter.setPen(origin_pen)
        painter.drawLine(-10, -10, 10, 10)
        painter.drawLine(-10, 10, 10, -10)

        scene_rect = self.scene().sceneRect()
        boundary_pen = QPen(QColor(255, 0, 0))
        boundary_pen.setWidth(10)
        painter.setPen(boundary_pen)
        painter.drawRect(scene_rect)

        from PySide6.QtGui import QBrush, QPixmap

        pix = QPixmap("./resources/StorageContainer.png")
        pen = QPen()
        pen.setWidth(10)
        brush = QBrush(pix)
        scale = pen.width() / pix.height()
        transform = QTransform()
        transform.scale(scale, scale)   # scale texture coordinates
        brush.setTransform(transform)
        pen.setBrush(brush)
        painter.setPen(pen)
        painter.drawLine(0, 0, 200, 0)
        painter.drawLine(200, 0, 200, 200)
