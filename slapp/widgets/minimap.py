from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve
from PySide6.QtGui import QPen, QColor, QBrush
from slapp.editor.clock import ClockSource

class MinimapView(QGraphicsView):

    def __init__(self, main_view: QGraphicsView, parent=None):
        super().__init__(parent)
        self.main_view = main_view
        self.setScene(main_view.scene())
        self.setRenderHints(main_view.renderHints())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setInteractive(False)

        ClockSource.get_clock('minimap_update_clock', 33).timeout.connect(
            lambda: self.viewport().update())

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

        # Map the main view's viewport rect to scene coordinates
        scene_rect = self.main_view.mapToScene(self.main_view.viewport().rect()).boundingRect()

        # Draw a rectangle showing the main view
        pen = QPen(QColor('#FD5602'))
        pen.setWidth(2)
        pen.setCosmetic(True)
        painter.setPen(pen)

        color = QColor('#FD5602')
        color.setAlphaF(0.1)
        brush = QBrush(color)
        painter.setBrush(brush)
        painter.drawRect(scene_rect)

        self.fitInView(self.main_view.sceneRect())

    def animate_center_on(self, target_scene_pos):
        view = self.main_view

        start = view.mapToScene(view.viewport().rect().center())

        self.anim = QVariantAnimation(self)
        self.anim.setDuration(700)
        self.anim.setStartValue(start)
        self.anim.setEndValue(target_scene_pos)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        def update(pos):
            view.centerOn(pos)

        self.anim.valueChanged.connect(update)
        self.anim.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            self.animate_center_on(scene_pos)
