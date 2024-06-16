import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QWidget, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QStyle

class IconGallery(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        # List of QStyle.StandardPixmap enumerations
        icon_names = [attr for attr in dir(QStyle) if attr.startswith('SP_')]

        for index, icon_name in enumerate(icon_names):
            pixmap = self.style().standardPixmap(getattr(QStyle, icon_name))
            icon_label = QLabel()
            icon_label.setPixmap(pixmap)
            text_label = QLabel(icon_name)

            layout.addWidget(icon_label, index // 4, (index * 2) % 8)
            layout.addWidget(text_label, index // 4, (index * 2) % 8 + 1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QStyle.SP_ Icons Gallery")
        self.setGeometry(100, 100, 800, 600)

        icon_gallery = IconGallery()
        self.setCentralWidget(icon_gallery)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
