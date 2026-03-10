import sys
from PySide6.QtWidgets import QApplication
from slapp.widgets.main_window import MainWindow
from slapp.resources.loader import ResourceLoader

def main():
    app = QApplication(sys.argv)
    with open(ResourceLoader.load(':/theme.qss'), mode='r') as theme_file:
        app.setStyleSheet(theme_file.read())

    main_window = MainWindow(app)
    main_window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()