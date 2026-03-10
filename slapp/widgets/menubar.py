from PySide6.QtWidgets import QWidget, QMenuBar

class Menubar(QMenuBar):

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)