from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtCore import Qt, QPointF

from view.Settings import Settings

class DraggableRectItem(QGraphicsPixmapItem):
    GRID_SIZE = Settings.PIXELS_PER_METER

    def __init__(self, x, y, w, h, pixmap):
        pixmap = pixmap.scaled(w, h)

        super().__init__(pixmap)
        
        rect = self.boundingRect()
        self.setOffset(-rect.width()/2, -rect.height()/2)
        self.setPos(
            x + rect.width()/2,
            y + rect.height()/2
        )

        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsGeometryChanges, True)
        self.setCursor(Qt.OpenHandCursor)

    def itemChange(self, change, value):    
        if change == QGraphicsPixmapItem.ItemPositionChange:
            snapped_x = round(value.x() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            snapped_y = round(value.y() / Settings.PIXELS_PER_METER) * Settings.PIXELS_PER_METER
            return QPointF(snapped_x, snapped_y)

        return super().itemChange(change, value)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)