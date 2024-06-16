from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('img/icon.png'))
        self.setWindowTitle('Alex MultiMedia')
        self.setGeometry(350, 100, 700, 500)

        # self.setStyleSheet("background-color: black;")
        # palette = self.palette()
        # palette.setColor(QPalette.Window, Qt.black)
        # self.setPalette(palette)

        self.init_player()

    def init_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.videoWidget = QVideoWidget()

        self.container = QWidget()
        self.video_layout = QVBoxLayout(self.container)
        self.video_layout.setContentsMargins(0, 0, 0, 0)
        self.video_layout.addWidget(self.videoWidget)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.create_controls()

        self.controls_container = QWidget(self.container)
        self.controls_container.setContentsMargins(0, 0, 0, 0)
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.addWidget(self.playBtn)
        self.controls_layout.addWidget(self.slider)
        self.controls_layout.addWidget(self.timeLabel)
        self.controls_layout.addWidget(self.closeControlsBtn)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.playing_state_handler)
        self.mediaPlayer.positionChanged.connect(self.position_handler)
        self.mediaPlayer.durationChanged.connect(self.duration_handler)

        self.central_widget.setLayout(self.layout)

        # Create a timer to update the playback time label
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # update every second
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start()

        # Connect events
        self.resizeEvent = self.resize_event_handler
        # self.container.enterEvent = self.enter_event_handler
        self.container.mousePressEvent = self.mouse_press_handler

    def create_controls(self):
        self.openBtn = QPushButton('Open Video', self.container)
        self.openBtn.clicked.connect(self.open_file)

        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)
        self.playBtn.setStyleSheet("margin: 20px;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.timeLabel = QLabel('00:00:00 / 00:00:00')
        self.timeLabel.setContentsMargins(20, 0, 0, 0)

        self.closeControlsBtn = QPushButton()
        self.closeControlsBtn.setIcon(self.style().standardIcon(QStyle.SP_TitleBarCloseButton))
        self.closeControlsBtn.clicked.connect(self.hide_controls)
        self.closeControlsBtn.setStyleSheet("margin: 20px;")

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open Video')

        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playBtn.setEnabled(True)
            self.play_video()
            self.hide_controls()

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def playing_state_handler(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_handler(self, position):
        self.slider.setValue(position)
        self.update_time_label()

    def duration_handler(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def resize_event_handler(self, event):
        self.controls_container.setGeometry(
            20, self.height() - 45, self.width() - 40, 30)

    def hide_controls(self):
        self.openBtn.hide()
        self.controls_container.hide()

    def show_controls(self):
        self.openBtn.show()
        self.controls_container.show()
        # QTimer.singleShot(15000, self.hide_controls)

    def mouse_press_handler(self, event):
        QTimer.singleShot(100, self.show_controls)

    def update_time_label(self):
        current_time = self.mediaPlayer.position()
        total_time = self.mediaPlayer.duration()
        formatted_time = f'{self.format_time(
            current_time)} / {self.format_time(total_time)}'
        self.timeLabel.setText(formatted_time)

    def format_time(self, ms):
        seconds = (ms / 1000) % 60
        minutes = (ms / (1000 * 60)) % 60
        hours = (ms / (1000 * 60 * 60)) % 24
        return "%02d:%02d:%02d" % (hours, minutes, seconds)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
