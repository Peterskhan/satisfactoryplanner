from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QStyle
from PySide6.QtCore import Qt

class SelectableGraphicsItem:
    def drawSelection(self, painter, option):
        if option.state & QStyle.State_Selected:
            highlight = QPen(QColor(0, 220, 255, 180), 3)
            highlight.setCosmetic(True)  # stays same width when zooming
            painter.setPen(highlight)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(self.shape())