from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPen, QColor

class MinimapView(QGraphicsView):

    def __init__(self, main_view: QGraphicsView, parent=None):
        super().__init__(parent)
        self.main_view = main_view
        self.setScene(main_view.scene())
        self.setRenderHints(main_view.renderHints())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.NoDrag)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.viewport().update())
        self.timer.start(33)  # Update at ~30 FPS

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        # Map the main view's viewport rect to scene coordinates
        scene_rect = self.main_view.mapToScene(self.main_view.viewport().rect()).boundingRect()
        
        # Draw a rectangle showing the main view
        pen = QPen(QColor('lightgray'))
        pen.setWidth(100)
        painter.setPen(pen)
        painter.drawRect(scene_rect)
