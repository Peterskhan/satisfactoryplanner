from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtCore import QPointF

from view.Settings import Settings

class DraggableRectItem(QGraphicsPixmapItem):
    GRID_SIZE = Settings.PIXELS_PER_METER

    def __init__(self, x, y, w, h, pixmap):
        pixmap = pixmap.scaled(w, h)

        super().__init__(pixmap)
        self.setPos(x, y)

        #rect = self.boundingRect()
        #self.setTransformOriginPoint(rect.width() / 2, rect.height() / 2)

        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsGeometryChanges, True)

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.ItemPositionChange:
            x = round(value.x() / self.GRID_SIZE) * self.GRID_SIZE
            y = round(value.y() / self.GRID_SIZE) * self.GRID_SIZE
            return QPointF(x, y)

        return super().itemChange(change, value)
    
        if change == QGraphicsPixmapItem.ItemPositionChange:
            snapped_x = round(value.x() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            snapped_y = round(value.y() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER

            return QPointF(snapped_x, snapped_y)

        return super().itemChange(change, value)