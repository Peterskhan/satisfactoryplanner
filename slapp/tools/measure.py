from enum import Enum

from PySide6.QtCore import Qt, QPointF, QLineF, QRectF
from PySide6.QtGui import QMouseEvent, QPen, QColor, QFont, QPainterPath
from PySide6.QtWidgets import QGraphicsPathItem

from slapp.editor.settings import Settings
from slapp.tools.tool_base import EditorTool, EditorContext


class MeasurementTool(EditorTool):
    context: EditorContext

    class State(Enum):
        DRAW = 1
        SHOW = 2

    def __init__(self, context: EditorContext) -> None:
        """Initialize the MeasurementTool."""
        self.context = context
        self.points = [self.snap(context.mouse_scene_position())]
        self.state = self.State.DRAW
        self.font = QFont("Arial", 64)
        self.path = QPainterPath()
        self.path_item = QGraphicsPathItem(self.path)
        self.path_item.setPen(QPen(QColor('lightgray'), 2))
        self.context.add_preview_item(self.path_item)
        self.draw_rulers()

    #region

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handles mouse press events."""
        if event.button() == Qt.LeftButton:
            match self.state:
                case self.State.DRAW:
                    if not self.points:
                        self.points.append(self.snap(event.scenePos()))
                    self.points.append(self.snap(event.scenePos()))
                case self.State.SHOW:
                    self.points.clear()
                    self.points.append(self.snap(event.scenePos()))
                    self.points.append(self.snap(event.scenePos()))
                    self.state = self.State.DRAW
            self.draw_rulers()

        elif event.button() == Qt.RightButton:
            match self.state:
                case self.State.DRAW:
                    self.state = self.State.SHOW
                    self.points.pop()
                    self.draw_rulers()
                case self.State.SHOW:
                    self.cancel()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.state == self.state.SHOW:
            return

        if not self.points:
            self.points.append(event.scenePos())

        self.points[-1] = self.snap(event.scenePos())
        self.draw_rulers()

    #endregion

    def draw_rulers(self):
        """Draw the ruler segments."""
        if not self.points:
            return

        self.path.clear()
        self.path.moveTo(self.points[0])

        for point in self.points:
            rect = QRectF(point - QPointF(5, 5), point + QPointF(5, 5))
            self.path.addRect(rect)

        lines = [QLineF(self.points[i], self.points[i+1]) for i in range(0, len(self.points) - 1)]
        for line in lines:
            midpoint = line.pointAt(0.5)
            midpoint += QPointF(10, -10)
            if line.length() > 0.001:
                self.path.addText(midpoint, self.font, f'{line.length() / Settings.PIXELS_PER_METER:.2f} m')
            self.path.moveTo(line.p1())
            self.path.lineTo(line.p2())

        self.path_item.setPath(self.path)

    def snap(self, pos: QPointF) -> QPointF:
        scale = Settings.PIXELS_PER_METER
        snapped_x = round(pos.x() / scale) * scale
        snapped_y = round(pos.y() / scale) * scale
        return QPointF(snapped_x, snapped_y)

    def cancel(self) -> None:
        self.context.remove_preview_item(self.path_item)
        self.context.exit_tool()
