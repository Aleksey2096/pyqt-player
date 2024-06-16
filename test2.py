import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Media Player Example")
        self.setGeometry(100, 100, 800, 600)

        # Create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        # Create video widget object
        self.videoWidget = QVideoWidget()

        # Create play button
        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon('play.png'))
        self.playButton.clicked.connect(self.play_pause)

        # Create a slider for media position
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        # Create a label to show current playback time
        self.timeLabel = QLabel('00:00:00')

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addWidget(self.slider)
        layout.addWidget(self.timeLabel)
        layout.addWidget(self.playButton)

        self.setLayout(layout)

        # Set the video output for the media player
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Connect signals
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

        # Create a timer to update the playback time label
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # update every second
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start()

    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def position_changed(self, position):
        self.slider.setValue(position)
        self.update_time_label()

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def update_time_label(self):
        current_time = self.mediaPlayer.position()
        formatted_time = self.format_time(current_time)
        self.timeLabel.setText(formatted_time)

    def format_time(self, ms):
        seconds = (ms / 1000) % 60
        minutes = (ms / (1000 * 60)) % 60
        hours = (ms / (1000 * 60 * 60)) % 24
        return "%02d:%02d:%02d" % (hours, minutes, seconds)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile("D://My documents//Downloads//Say.It.Isn't.So.2001.1080p.WEBRip.x264.AAC-[YTS.MX].mp4")))  # Set your media file path here
    player.show()
    sys.exit(app.exec_())



