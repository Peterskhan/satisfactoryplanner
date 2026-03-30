from PySide6.QtGui import QPixmap, QPainterPath, QTransform, QBrush, QColor
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QStyle, QGraphicsPixmapItem
from PySide6.QtCore import Qt, QPointF
from slapp.items.selectable import SelectableGraphicsItem
from slapp.editor.settings import Settings
from slapp.core.discrete import BuildingType, DiscreteElement

class DiscreteItem(QGraphicsPixmapItem, SelectableGraphicsItem):
    type: BuildingType

    def __init__(self, instance: DiscreteElement):
        scale = Settings.PIXELS_PER_METER
        width = instance.type.width * scale
        height = instance.type.length * scale
        super().__init__(QPixmap(instance.type.texture).scaled(width, height))

        rect = self.boundingRect()
        self.setOffset(-rect.width()/2, -rect.height()/2)

        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.OpenHandCursor)

        self.instance = instance
        self.instance.position_changed.connect(self.update_from_model)
        self.instance.rotation_changed.connect(self.update_from_model)
        self.update_from_model()

    def update_from_model(self):
        """Update the visual representation of the building based on its model data."""
        self.setPos(self.instance.position * Settings.PIXELS_PER_METER)
        self.setRotation(self.instance.rotation)
        self.update()

    def snapped_position(self, position: QPointF) -> QPointF:
        scale = Settings.PIXELS_PER_METER
        if self.instance.type.snap_center:
            return QPointF(round(position.x() / scale) * scale,
                           round(position.y() / scale) * scale)
        else:
            top_left_scene = self.mapToScene(self.boundingRect().topLeft())
            delta = top_left_scene - self.pos()
            proposed_top_left = position + delta
            snapped_top_left = QPointF(
                round(proposed_top_left.x() / scale) * scale,
                round(proposed_top_left.y() / scale) * scale
            )

            return snapped_top_left - delta

    def itemChange(self, change, value):

        # Snapping to grid
        if change == DiscreteItem.ItemPositionChange:
            return self.snapped_position(value)

        # Updating model
        if change == DiscreteItem.ItemPositionHasChanged:
            self.instance.move_to(value / Settings.PIXELS_PER_METER)

        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def shape(self):
        path = super().shape()
        path = path.toFillPolygon().boundingRect().adjusted(0.1, 0.1, -0.1, -0.1)
        new_path = QPainterPath()
        new_path.addRect(path)
        return new_path

    def is_colliding(self) -> bool:
        return len(self.collidingItems()) > 0

    @staticmethod
    def rotate_point(point, degrees):
        transform = QTransform().rotate(degrees)
        return transform.map(point)

    def paint(self, painter, option, widget):
        opt = QStyleOptionGraphicsItem(option)
        opt.state &= ~QStyle.State_Selected
        super().paint(painter, opt, widget)
        if option.state & QStyle.State_Selected:
            self.drawSelection(painter, option)

        if self.instance.type.power_connection:
            painter.setBrush(QBrush(QColor("red")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.instance.type.power_connection * Settings.PIXELS_PER_METER, 20, 20)

        if self.instance.type.output_positions:
            for position in self.instance.type.output_positions:
                painter.setBrush(QBrush(QColor("green")))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(position * Settings.PIXELS_PER_METER, 20, 20)

        if self.instance.type.input_positions:
            for position in self.instance.type.input_positions:
                painter.setBrush(QBrush(QColor("orange")))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(position * Settings.PIXELS_PER_METER, 20, 20)
