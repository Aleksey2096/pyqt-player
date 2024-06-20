import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Hide Cursor Example')
        self.setGeometry(100, 100, 800, 600)

        # Timer to hide the cursor
        self.hideCursorTimer = QTimer(self)
        self.hideCursorTimer.timeout.connect(self.hideCursor)

        # Timeout period in milliseconds (e.g., 2000 ms = 2 seconds)
        self.inactivityTimeout = 2000
        self.hideCursorTimer.start(self.inactivityTimeout)

        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        # Reset the timer on mouse movement
        self.hideCursorTimer.start(self.inactivityTimeout)
        # Show the cursor when it moves
        self.setCursor(Qt.ArrowCursor)

    def hideCursor(self):
        # Hide the cursor
        self.setCursor(Qt.BlankCursor)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
