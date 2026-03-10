from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QApplication
from PySide6.QtCore import QTimer

class SceneDebugWindow(QWidget):
    def __init__(self, scene):
        """
        main_window: your main editor window that has a 'scene' attribute
        """
        super().__init__()
        self.setWindowTitle("Scene Debugger")
        self.resize(400, 600)
        self.scene = scene

        # Text area to display debug info
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # Timer for periodic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_debug)
        self.timer.start(500)  # update every 0.5 seconds

        self.text_lines = []

    def debug_print(self, *args):
        # Convert all args to string and join with spaces
        line = " ".join(str(arg) for arg in args)
        self.text_lines.append(line)

    def update_debug(self):
        self.text_lines = []
        self.text_area.setPlainText("\n".join(self.text_lines))


# Example usage:
# debug_window = SceneDebugWindow(main_window)
# debug_window.show()