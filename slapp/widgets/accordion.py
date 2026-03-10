from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QVBoxLayout, QApplication, QFrame, QSizePolicy, QScrollArea, QSpacerItem
from PySide6.QtGui import QPixmap, QKeyEvent, QPainter
from PySide6.QtCore import Qt, QObject, QPropertyAnimation, QVariantAnimation, QEasingCurve
import sys

class RotatingLabel(QLabel):
    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self._rotation = 0
        self.setPixmap(pixmap)
        self.setScaledContents(True)

    def rotate(self, angle_deg: float) -> None:
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(500)
        self.anim.setStartValue(self._rotation)
        self.anim.setEndValue(angle_deg)
        self.anim.setEasingCurve(QEasingCurve.Type.OutExpo)

        def update(rotation: float):
            self._rotation = rotation

        self.anim.valueChanged.connect(update)
        self.anim.start()

    def paintEvent(self, _):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        rect = self.rect()
        cx = rect.center().x()
        cy = rect.center().y()

        painter.translate(cx, cy)
        painter.rotate(self._rotation)
        painter.translate(-cx, -cy)

        painter.drawPixmap(rect, self.pixmap())

class AccordionHeader(QFrame):

    def __init__(self, title: str, *, icon: QPixmap = None, badge: QPixmap = None) -> None:
        super().__init__()

        self.icon = QLabel()
        self.icon.setObjectName('icon')
        if icon:
            self.icon.setPixmap(icon)
            self.icon.setFixedSize(16, 16)
            self.icon.setScaledContents(True)

        self.title = QLabel(title)
        self.title.setObjectName('title')

        self.badge = QLabel()
        self.badge.setObjectName('badge')
        if badge:
            self.badge.setPixmap(badge)
            self.badge.setFixedSize(16, 16)
            self.badge.setScaledContents(True)

        self.chevron = RotatingLabel(QPixmap('slapp/resources/icons/chevron_forward.svg'))
        self.chevron.setFixedSize(16, 16)
        self.chevron.setObjectName('chevron')

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.icon)
        main_layout.addWidget(self.title)
        main_layout.addStretch()
        main_layout.addWidget(self.badge)
        main_layout.addWidget(self.chevron)

        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

    def set_icon(self) -> None:
        pass

    def set_title(self) -> None:
        pass

    def set_badge(self) -> None:
        pass

    def set_chevron(self) -> None:
        pass

    def rotate_chevron(self, angle_deg: float) -> None:
        self.chevron.rotate(angle_deg)

    def set_subtitle(self) -> None:
        pass

class AccordionContainer(QWidget):

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

    def add_content(self, content: QWidget) -> None:
        self.layout().addWidget(content)

class AccordionSection(QFrame):

    def __init__(self, title: str, content: QWidget, *, icon: QPixmap = None, badge: QPixmap = None) -> None:
        super().__init__()

        self.header = AccordionHeader(title, icon=icon, badge=badge)
        self.header.setObjectName('header')

        self.content_container = AccordionContainer()
        self.content_container.setMaximumHeight(0)
        self.content_container.setObjectName('content')

        if content:
            self.content_container.add_content(content)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.addWidget(self.header)
        main_layout.addWidget(self.content_container)

        self.setLayout(main_layout)
        self.is_collapsed = True

    def set_collapsed(self, collapsed: bool) -> None:
        self.anim = QPropertyAnimation(self.content_container, b'maximumHeight')
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setStartValue(self.content_container.height())
        self.anim.setEndValue(0 if collapsed else self.content_container.sizeHint().height())
        self.anim.start()

        def on_finished():
            self.content_container.setMaximumHeight(0 if collapsed else 9999)
            self.update()

        self.anim.finished.connect(on_finished)
        self.header.rotate_chevron(0 if collapsed else 90)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_collapsed = not self.is_collapsed
            self.set_collapsed(self.is_collapsed)

        return super().mousePressEvent(event)

class Accordion(QFrame):

    def __init__(self) -> None:
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(main_layout)

    def add_section(self, title: str, content: QWidget, *, icon: QPixmap = None, badge: QPixmap = None):
        self.layout().addWidget(AccordionSection(title, content, icon=icon, badge=badge))
