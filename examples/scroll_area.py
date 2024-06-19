import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QScrollArea, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QLabel to hold the QPixmap
        self.label = QLabel()
        self.pixmap = QPixmap("D:/My documents/Downloads/Pictures/Glanced/0.jpeg")
        self.label.setPixmap(self.pixmap)

        # Create a QScrollArea and set the QLabel as its widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)

        # Set the scroll area as the central widget of the main window
        self.setCentralWidget(self.scroll_area)

        # Set the window title and size
        self.setWindowTitle("Resizable Image Viewer")
        self.resize(800, 600)  # Initial size of the window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
