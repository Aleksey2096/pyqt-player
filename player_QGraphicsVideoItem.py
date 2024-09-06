import sys
import os
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QSizeF
from PyQt6.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt6.QtGui import QIcon


# Transforms relative path to absolute path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# app constants
app_name = 'Alex MultiMedia'


class ControlsBar(QWidget):
    def __init__(self):
        super().__init__()

        # Applies a transparent background color
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        # Creates a layout and adds controls
        self.controls_layout = QHBoxLayout()
        self.controls_layout.addWidget(QPushButton("Button 1"))
        self.controls_layout.addWidget(QPushButton("Button 2"))
        self.controls_layout.addWidget(QPushButton("Button 3"))

        self.main_layout = QVBoxLayout()
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.progress_slider)
        self.main_layout.addLayout(self.controls_layout)

        # Sets the layout for the widget
        self.setLayout(self.main_layout)


class MediaPlayer(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path('img/app_icon.ico')))
        self.setWindowTitle(app_name)
        self.setGeometry(320, 180, 960, 540)
        self.setBackgroundBrush(Qt.GlobalColor.black)
        # Removes white border around QGraphicsView
        self.setFrameStyle(0)

        # Creates a scene to hold the video item
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Creates a QGraphicsVideoItem and adds it to the scene
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        # Creates a ControlsBar and adds it to the scene
        self.controls_bar = ControlsBar()
        self.scene.addWidget(self.controls_bar)

        # Creates a media player and audio output and sets the video and audio outputs
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_item)

        # Loads and plays a video file
        self.media_player.setSource(QUrl.fromLocalFile('D:/My documents/Downloads/American Pie 1999.mp4'))
        self.media_player.play()

        # Disables scrollbars (during resizing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resizes video item to fit the view
        self.setSceneRect(0, 0, self.width(), self.height())
        self.video_item.setSize(QSizeF(self.size()))
        # Resizes ControlsBar to stay at the bottom of the screen
        self.controls_bar.setGeometry(20, self.height() - 75, self.width() - 40, 60)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())
