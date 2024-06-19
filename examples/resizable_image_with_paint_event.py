import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

# Custom label allows to resize image inside of it while keeping aspect ratio
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()

    def setPixmap(self, pixmap_path):
        if not self.pixmap.load(pixmap_path):
            print("Failed to load pixmap:", pixmap_path)
        self.update()

    def paintEvent(self, event):
        print('ImageLabel resized')
        painter = QPainter(self)
        rect = self.rect()
        scaled_pixmap = self.pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        point = rect.center() - scaled_pixmap.rect().center()
        painter.drawPixmap(point, scaled_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a custom QLabel to hold the QPixmap
        self.label = ImageLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setPixmap("D:/My documents/Downloads/Pictures/Glanced/0.jpeg")

        # Set the ImageLabel as the central widget of the main window
        self.setCentralWidget(self.label)

        # Set the window title and size
        self.setWindowTitle("Resizable Image Viewer with QPixmap")
        self.resize(800, 600)  # Initial size of the window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
