import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimerEvent,QTimer

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.singleClick)

    def initUI(self):
        self.label = QLabel("Click or double-click anywhere in the window", self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)

        self.setLayout(vbox)

        self.setWindowTitle('Single and Double Click Event Example')
        self.setGeometry(100, 100, 400, 300)
        self.show()

    def mousePressEvent(self, event):
        # Start the timer on mouse press
        if not self.timer.isActive():
            self.timer.start(250)  # 250 ms delay to differentiate single click from double click

    def singleClick(self):
        # This method will be called if no double click is detected within the delay
        self.label.setText('Mouse single-clicked')
        print('Mouse single-clicked')

    def mouseDoubleClickEvent(self, event):
        # Stop the single click timer if a double click is detected
        if self.timer.isActive():
            self.timer.stop()
        x = event.x()
        y = event.y()
        self.label.setText(f'Mouse double-clicked at ({x}, {y})')
        print(f'Mouse double-clicked at ({x}, {y})')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

