from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPathStroker, QPainterPath
from PySide6.QtCore import Qt, QPointF, QRectF
from slapp.editor.settings import Settings
from slapp.editor.clock import ClockSource
from slapp.editor.items.selectable import SelectableGraphicsItem
from slapp.core.linear import LinearElement
import math

def build_path(points, ppm, radius_units=1):

    def unit(vx, vy):
        length = math.hypot(vx, vy)
        return vx / length, vy / length

    def angle(vx, vy):
        return math.degrees(math.atan2(-vy, vx))

    path = QPainterPath()
    points = [QPointF(p.x, p.y) * ppm for p in points]
    if not points:
        return path

    path.moveTo(points[0])
    for i in range(1, len(points)-1):
        A = points[i-1]
        B = points[i]
        C = points[i+1]
        r = ppm * radius_units

        # Raw direction vectors (pixel coordinates)
        dx1 = B.x() - A.x()
        dy1 = B.y() - A.y()
        dx2 = C.x() - B.x()
        dy2 = C.y() - B.y()

        # Skip degenerate segments
        if (abs(dx1) < 1e-9 and abs(dy1) < 1e-9) or (abs(dx2) < 1e-9 and abs(dy2) < 1e-9):
            path.lineTo(B)
            continue

        # Draw an arc only for (approximately) 90° turns. For straight or non-90° turns, draw a straight corner.
        dot = dx1 * dx2 + dy1 * dy2
        if abs(dot) < 1e-6:
            v1x, v1y = unit(dx1, dy1)
            v2x, v2y = unit(dx2, dy2)

            p1 = QPointF(B.x() - v1x * r, B.y() - v1y * r)
            p2 = QPointF(B.x() + v2x * r, B.y() + v2y * r)
            path.lineTo(p1)

            cx = p1.x() + v2x * r
            cy = p1.y() + v2y * r
            rect = QRectF(cx - r, cy - r, 2*r, 2*r)
            start = angle(p1.x() - cx, p1.y() - cy)
            end = angle(p2.x() - cx, p2.y() - cy)
            sweep = end - start

            if sweep > 180:
                sweep -= 360
            elif sweep < -180:
                sweep += 360

            path.arcTo(rect, start, sweep)
        else:
            path.lineTo(B)

    path.lineTo(points[-1])
    return path

class LinearItem(QGraphicsPathItem, SelectableGraphicsItem):
    def __init__(self, instance: LinearElement, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsPathItem.ItemIsSelectable | QGraphicsPathItem.ItemIsFocusable)
        self.width = Settings.PIXELS_PER_METER * (instance.type.width - 0.5)
        self.instance = instance
        self.phase = 0

        self.setPen(Qt.NoPen)  # we paint manually
        path = build_path(self.instance.nodes(), Settings.PIXELS_PER_METER)
        self.setPath(path)

        ClockSource.get_clock('conveyor_animation_clock', 33).timeout.connect(self.animate)

    def update_from_instance(self):
        path = build_path(self.instance.nodes(), Settings.PIXELS_PER_METER)
        self.setPath(path)

    def animate(self):
        self.phase = self.phase - 0.01
        self.update()

    def _body_path(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(self.width)
        stroker.setCapStyle(Qt.FlatCap)
        return stroker.createStroke(self.path())

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        # --- 1️⃣ Fill belt body ---
        body = self._body_path()
        painter.fillPath(body, QColor('#202020'))

        # --- 2️⃣ Draw edges ---
        edge_pen = QPen(QColor(120, 120, 120), 10)
        edge_pen.setCapStyle(Qt.FlatCap)
        painter.setPen(edge_pen)
        painter.drawPath(body)

        pen = QPen(QColor("#6B6767"), 100)
        pen.setCapStyle(Qt.FlatCap)
        pen.setStyle(Qt.CustomDashLine)
        pen.setDashPattern([0.05, 0.3])  # 10 px dash, 10 px gap
        pen.setDashOffset(self.phase)  # marching effect
        painter.setPen(pen)
        painter.drawPath(self.path())

        self.drawSelection(painter, option)
        pen = QPen(QColor(200, 200, 200), 20)
        painter.setPen(pen)
        for node in self.instance.nodes():
            pos = QPointF(node.x * Settings.PIXELS_PER_METER, node.y * Settings.PIXELS_PER_METER)
            painter.drawPoint(pos)

    def shape(self):
        return self._body_path()

    def boundingRect(self):
        half = self.width * 0.5 + 10
        rect = self.path().boundingRect()
        rect.adjust(-half, -half, half, half)
        return rect

    def is_colliding(self) -> bool:
        return len(self.collidingItems()) > 0

