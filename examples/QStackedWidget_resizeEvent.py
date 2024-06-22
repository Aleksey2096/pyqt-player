import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget

class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create the stacked widget
        self.stackedWidget = QStackedWidget()

        # Create the first widget
        self.widget1 = QWidget()
        self.layout1 = QVBoxLayout()
        self.label1 = QLabel("Widget 1: This is the vertical layout")
        self.button1 = QPushButton("Button in Vertical Layout")
        self.layout1.addWidget(self.label1)
        self.layout1.addWidget(self.button1)
        self.widget1.setLayout(self.layout1)

        # Create the second widget
        self.widget2 = QWidget()
        self.layout2 = QVBoxLayout()
        self.label2 = QLabel("Widget 2: This is the horizontal layout")
        self.button2 = QPushButton("Button in Horizontal Layout")
        self.layout2.addWidget(self.label2)
        self.layout2.addWidget(self.button2)
        self.widget2.setLayout(self.layout2)

        # Add widgets to the stacked widget
        self.stackedWidget.addWidget(self.widget1)
        self.stackedWidget.addWidget(self.widget2)

        # Create the main layout
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.stackedWidget)
        self.setLayout(self.mainLayout)

        # Initial size and title
        self.setGeometry(100, 100, 400, 300)
        self.setWindowTitle('QStackedWidget Example')
        self.show()

    def resizeEvent(self, event):
        width = event.size().width()

        # Switch widgets based on window width
        if width > 500:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

        print(f'Window resized to ({width}, {event.size().height()})')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
