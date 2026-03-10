from PySide6.QtCore import Qt, Signal, QSize, QPoint
from PySide6.QtWidgets import QWidget, QScrollArea, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QToolButton, QSizePolicy
from PySide6.QtGui import QIcon, QPixmap, QFont
from slapp.core.floor import Floor
from slapp.resources.loader import ResourceLoader

class DragHandle(QLabel):

    def __init__(self, parent_widget):
        super().__init__()
        self.parent_widget = parent_widget
        self.drag_start_pos = QPoint()
        self.setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self.drag_start_pos
            self.parent_widget.move(self.parent_widget.pos() + delta)
            self.drag_start_pos = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

class FloorFrame(QFrame):

    add_above_clicked = Signal(object)
    add_below_clicked = Signal(object)
    delete_clicked = Signal(object)
    selected = Signal(object)

    def __init__(self, index: int, floor: Floor) -> None:
        super().__init__()
        self.setObjectName("floorFrame")
        self.setContentsMargins(0, 0, 0, 0)

        self.index = index
        self.floor = floor
        self.selected_flag = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setFixedWidth(150)

        self.label = QLabel(f"FLOOR {index:02d}")
        self.label.setFont(QFont("Consolas", 12))
        self.label.setStyleSheet("background: transparent;")

        layout.addWidget(self.label)
        layout.addStretch()

        self.delete_button = QToolButton()
        self.delete_button.setIcon(QIcon(ResourceLoader.load(':/icons/delete.svg')))
        self.delete_button.setFixedSize(QSize(16, 16))
        self.delete_button.clicked.connect(lambda: self.delete_clicked.emit(self))
        layout.addWidget(self.delete_button)

        self.add_below_button = QToolButton()
        self.add_below_button.setIcon(QIcon(ResourceLoader.load(":/icons/add_row_below.svg")))
        self.add_below_button.setFixedSize(QSize(16, 16))
        self.add_below_button.clicked.connect(lambda: self.add_below_clicked.emit(self))
        layout.addWidget(self.add_below_button)

        self.add_above_button = QToolButton()
        self.add_above_button.setIcon(QIcon(ResourceLoader.load(":/icons/add_row_above.svg")))
        self.add_above_button.setFixedSize(QSize(16, 16))
        self.add_above_button.clicked.connect(lambda: self.add_above_clicked.emit(self))
        layout.addWidget(self.add_above_button)

        self.delete_button.hide()
        self.add_below_button.hide()
        self.add_above_button.hide()

        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.update_style()

    def set_selected(self, selected: bool):
        self.selected_flag = selected
        self.update_style()

    def update_style(self):
        if self.selected_flag:
            # Active floor: full orange background
            self.setStyleSheet("""
                #floorFrame {
                    background-color: #ff9c33;
                    border: 1px solid #ff9c33;
                    border-radius: 1px;
                }
            """)
        else:
            # Normal + hover border
            self.setStyleSheet("""
                #floorFrame {
                    background-color: #2b2b2b;
                    border: 1px solid transparent;
                    border-radius: 1px;
                }
                #floorFrame:hover {
                    border: 1px solid #ff9c33;
                    background-color: #2b2b2b;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected.emit(self)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.delete_button.show()
        self.add_below_button.show()
        self.add_above_button.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.delete_button.hide()
        self.add_below_button.hide()
        self.add_above_button.hide()
        super().leaveEvent(event)

class FloorSelector(QFrame):

    floor_changed = Signal(Floor)

    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setObjectName("floorSelector")

        self.scene = scene
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAutoFillBackground(True)
        self.setMinimumHeight(200)

        # Title
        title_layout = QHBoxLayout()

        drag_handle = DragHandle(self)
        drag_handle.setPixmap(
            QPixmap(ResourceLoader.load(":/icons/drag_indicator.svg")).scaled(16, 16)
        )
        drag_handle.setCursor(Qt.OpenHandCursor)

        title_label = QLabel("Factory Floors")

        title_layout.addWidget(drag_handle)
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        main_layout.addLayout(title_layout)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.content)

        main_layout.addWidget(self.scroll_area)
        self.refresh()

        self.setObjectName("floorSelector")
        self.scroll_area.setObjectName("floorScrollArea")
        self.content.setObjectName("floorList")
        title_label.setObjectName("floorTitle")
        drag_handle.setObjectName("floorDragHandle")

    def refresh(self):
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()

        for index, floor in enumerate(self.scene.factory.floors):
            frame = self._add_floor_widget(index, floor)
            if floor == self.scene.active_floor():
                frame.set_selected(True)

    def _add_floor_widget(self, index: int, floor: Floor) -> FloorFrame:
        frame = FloorFrame(index, floor)
        frame.add_above_clicked.connect(self._on_add_floor_above)
        frame.add_below_clicked.connect(self._on_add_floor_below)
        frame.delete_clicked.connect(self._on_floor_deleted)
        frame.selected.connect(self._on_floor_selected)
        self.content_layout.insertWidget(1, frame)
        return frame

    def _on_floor_selected(self, frame: FloorFrame):
        self.floor_changed.emit(frame.floor)
        self.refresh()

    def _on_floor_deleted(self, frame: FloorFrame):
        self.scene.factory.remove_floor(frame.index)
        self.refresh()

    def _on_add_floor_below(self, frame: FloorFrame):
        self.scene.factory.add_floor(frame.index)
        self.refresh()

    def _on_add_floor_above(self, frame: FloorFrame):
        self.scene.factory.add_floor(frame.index + 1)
        self.refresh()