from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog, \
    QMainWindow, QLabel, QShortcut
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QKeySequence
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import sys
import os


# Transforms relative path to absolute path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Custom slider allows to instantly move handle to the current mouse click position
class VolumeSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(orientation, parent)

    def mousePressEvent(self, event):
        super(VolumeSlider, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
            self.setValue(value)
            event.accept()


app_name = 'Alex MultiMedia'


class MainWindow(QMainWindow):

    def __init__(self, file_path=None):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path('img/app_icon.ico')))
        self.setWindowTitle(app_name)
        self.setGeometry(320, 180, 960, 540)

        # self.setStyleSheet("background-color: black;")
        # palette = self.palette()
        # palette.setColor(QPalette.Window, Qt.black)
        # self.setPalette(palette)

        self.init_player()

        if file_path:
            self.play_file(file_path)

    def init_player(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.container = QWidget()
        self.media_layout = QVBoxLayout(self.container)
        self.media_layout.setContentsMargins(0, 0, 0, 0)
        # Widget to show output for video files
        self.video_widget = QVideoWidget()
        self.media_layout.addWidget(self.video_widget)
        # Label to show output (album cover image) for music files
        self.image_label = QLabel()
        self.media_layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.create_controls()

        self.controls_container = QWidget(self.container)
        self.controls_container.setContentsMargins(0, 0, 0, 0)
        self.controls_layout = QHBoxLayout(self.controls_container)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.addWidget(self.playBtn)
        self.controls_layout.addWidget(self.replay10btn)
        self.controls_layout.addWidget(self.forward30btn)
        self.controls_layout.addWidget(self.position_slider)
        self.controls_layout.addWidget(self.timeLabel)
        self.controls_layout.addWidget(self.volume_slider)
        self.controls_layout.addWidget(self.volume_label)
        self.controls_layout.addWidget(self.fullScreenBtn)
        self.controls_layout.addWidget(self.hideControlsBtn)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.container)

        self.mediaPlayer.setVideoOutput(self.video_widget)

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
        self.container.mousePressEvent = self.mouse_press_handler
        self.mediaPlayer.stateChanged.connect(self.playing_state_handler)
        self.mediaPlayer.positionChanged.connect(self.position_handler)
        self.mediaPlayer.durationChanged.connect(self.duration_handler)

    def create_controls(self):
        # Open File button
        self.openBtn = QPushButton('    Open File', self.container)
        self.openBtn.setIcon(QIcon(resource_path('img/file_open.png')))
        self.openBtn.clicked.connect(self.find_file)

        # Play/Stop button
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(QIcon(resource_path('img/play.png')))
        self.playBtn.setIconSize(QSize(30, 30))
        self.playBtn.clicked.connect(self.play)
        self.playBtn.setStyleSheet("margin: 20px 0 20px 20px;")
        # Play/Stop shortcut - 'Space'
        self.play_shortcut = QShortcut(Qt.Key_Space, self)
        self.play_shortcut.activated.connect(self.play)

        # Replay 10 seconds button
        self.replay10btn = QPushButton()
        self.replay10btn.setEnabled(False)
        self.replay10btn.setIcon(QIcon(resource_path('img/replay_10.png')))
        self.replay10btn.setIconSize(QSize(25, 25))
        self.replay10btn.clicked.connect(lambda: self.rewind_media(10500))
        self.replay10btn.setStyleSheet("margin: 20px 0;")
        # Replay 1 minute shortcut - 'Arrow Left'
        self.replay_minute_shortcut = QShortcut(Qt.Key_Left, self)
        self.replay_minute_shortcut.activated.connect(lambda: self.rewind_media(60500))

        # Forward 30 seconds button
        self.forward30btn = QPushButton()
        self.forward30btn.setEnabled(False)
        self.forward30btn.setIcon(QIcon(resource_path('img/forward_30.png')))
        self.forward30btn.setIconSize(QSize(25, 25))
        self.forward30btn.clicked.connect(lambda: self.forward_media(30000))
        self.forward30btn.setStyleSheet("margin: 20px 20px 20px 0;")
        # Forward 1 minute shortcut - 'Arrow Right'
        self.forward_minute_shortcut = QShortcut(Qt.Key_Right, self)
        self.forward_minute_shortcut.activated.connect(lambda: self.forward_media(60000))

        # Position slider
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        # Position label
        self.timeLabel = QLabel('00:00:00 / 00:00:00')
        self.timeLabel.setContentsMargins(10, 0, 20, 0)

        # Volume slider
        self.volume_slider = VolumeSlider()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(self.volume_handler)

        # Volume label
        self.volume_label = QLabel("50%", self)
        self.volume_label.setFixedWidth(56)
        self.volume_label.setStyleSheet("margin-left: 10px;")

        # FullScreen mode button
        self.fullScreenBtn = QPushButton()
        self.fullScreenBtn.setIcon(QIcon(resource_path('img/fullscreen.png')))
        self.fullScreenBtn.setIconSize(QSize(20, 20))
        self.fullScreenBtn.clicked.connect(self.screen_mode_handler)
        self.fullScreenBtn.setStyleSheet("margin: 20px 0px 20px 20px;")

        # Hide Controls button
        self.hideControlsBtn = QPushButton()
        self.hideControlsBtn.setIcon(QIcon(resource_path('img/hide.png')))
        self.hideControlsBtn.setIconSize(QSize(20, 20))
        self.hideControlsBtn.clicked.connect(self.hide_controls)
        self.hideControlsBtn.setStyleSheet("margin: 20px;")
        # Hide Controls shortcut - 'Arrow Down'
        self.hide_controls_shortcut = QShortcut(Qt.Key_Down, self)
        self.hide_controls_shortcut.activated.connect(self.hide_controls)
        # Show Controls shortcut - 'Arrow Up'
        self.show_controls_shortcut = QShortcut(Qt.Key_Up, self)
        self.show_controls_shortcut.activated.connect(self.show_controls)

    def find_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File')

        self.play_file(file_path)

    def play_file(self, file_path):
        if file_path != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.enable_controls()

            if file_path.endswith('.mp3'):
                self.image_label.show()
                self.video_widget.hide()
                self.display_album_cover(file_path)
            else:
                self.image_label.hide()
                self.video_widget.show()

            self.play()
            self.hide_controls()
            self.setWindowTitle(f'{app_name} - {os.path.basename(file_path)}')

    def display_album_cover(self, file_path):
        audio = MP3(file_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                pixmap = QPixmap()
                pixmap.loadFromData(tag.data)
                self.image_label.setPixmap(pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                break

    def enable_controls(self):
        self.playBtn.setEnabled(True)
        self.replay10btn.setEnabled(True)
        self.forward30btn.setEnabled(True)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def playing_state_handler(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(QIcon(resource_path('img/pause.png')))
        else:
            self.playBtn.setIcon(QIcon(resource_path('img/play.png')))

    def position_handler(self, position):
        self.position_slider.setValue(position)
        self.update_time_label()

    def duration_handler(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def resize_event_handler(self, event):
        self.controls_container.setGeometry(20, self.height() - 45, self.width() - 40, 30)

    def hide_controls(self):
        self.openBtn.hide()
        self.controls_container.hide()

    def show_controls(self):
        self.openBtn.show()
        self.controls_container.show()

    def mouse_press_handler(self, event):
        QTimer.singleShot(100, self.show_controls)

    def update_time_label(self):
        current_time = self.mediaPlayer.position()
        total_time = self.mediaPlayer.duration()
        formatted_time = f'{self.format_time(current_time)} / {self.format_time(total_time)}'
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
            self.fullScreenBtn.setIcon(QIcon(resource_path('img/fullscreen.png')))
        else:
            self.showFullScreen()
            self.fullScreenBtn.setIcon(QIcon(resource_path('img/fullscreen_exit.png')))

    def volume_handler(self, value):
        self.mediaPlayer.setVolume(value)
        self.volume_label.setText(f'{value}%')

    def rewind_media(self, rewind_time):
        current_position = self.mediaPlayer.position()
        new_position = max(0, current_position - rewind_time)
        self.mediaPlayer.setPosition(new_position)

    def forward_media(self, forward_time):
        current_position = self.mediaPlayer.position()
        duration = self.mediaPlayer.duration()
        new_position = current_position + forward_time
        if new_position >= duration:
            new_position = duration - 1000
        self.mediaPlayer.setPosition(new_position)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # sys argument allows to open files with this desktop app
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    window = MainWindow(file_path)

    window.show()
    sys.exit(app.exec_())
