from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer,QSize
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('img/app_icon.png'))
        self.setWindowTitle('Alex MultiMedia')
        self.setGeometry(320, 180, 960, 540)

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
        self.controls_layout.addWidget(self.fullScreenBtn)
        self.controls_layout.addWidget(self.hideControlsBtn)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.playing_state_handler)
        self.mediaPlayer.positionChanged.connect(self.position_handler)
        self.mediaPlayer.durationChanged.connect(self.duration_handler)

        self.central_widget.setLayout(self.layout)

        self.central_widget.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            QPushButton {
                font-size: 11px;
            }
        """)

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
        self.openBtn = QPushButton('    Open File', self.container)
        self.openBtn.setIcon(QIcon('img/file_open.png'))
        self.openBtn.clicked.connect(self.open_file)

        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setIconSize(QSize(25,25))
        self.playBtn.clicked.connect(self.play_video)
        self.playBtn.setStyleSheet("margin: 20px;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.timeLabel = QLabel('00:00:00 / 00:00:00')
        self.timeLabel.setContentsMargins(20, 0, 0, 0)

        self.fullScreenBtn = QPushButton()
        self.fullScreenBtn.setIcon(QIcon('img/fullscreen.png'))
        self.fullScreenBtn.setIconSize(QSize(20,20))
        self.fullScreenBtn.clicked.connect(self.screen_mode_handler)
        self.fullScreenBtn.setStyleSheet("margin: 20px 0px 20px 20px;")

        self.hideControlsBtn = QPushButton()
        self.hideControlsBtn.setIcon(QIcon('img/hide.png'))
        self.hideControlsBtn.setIconSize(QSize(20,20))
        self.hideControlsBtn.clicked.connect(self.hide_controls)
        self.hideControlsBtn.setStyleSheet("margin: 20px;")

    def open_file(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Open File')

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
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

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
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.screen_mode_handler()
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showMaximized()

    # toggle between normal and full-screen mode
    def screen_mode_handler(self):
        if self.isFullScreen():
            self.showNormal()
            self.fullScreenBtn.setIcon(QIcon('img/fullscreen.png'))
        else:
            self.showFullScreen()
            self.fullScreenBtn.setIcon(QIcon('img/fullscreen_exit.png'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
