import sys
from PySide6.QtWidgets import QApplication
from slapp.view.widgets.MainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()