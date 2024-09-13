from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QStyle, QSlider, QFileDialog,
                             QMainWindow, QLabel, QShortcut, QSizePolicy)
from PyQt5.QtGui import QIcon, QPixmap, QPainter
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer, QSize, QEvent
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4, MP4Cover
from mutagen.flac import FLAC
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


# Custom label allows to resize image inside of it while keeping aspect ratio
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap()

    def setPixmap(self, tag_data):
        if not self.pixmap.loadFromData(tag_data):
            print("Failed to load pixmap:", tag_data)
        self.update()

    def setPixmapPath(self, pixmap_path):
        if not self.pixmap.load(pixmap_path):
            print("Failed to load pixmap:", resource_path(pixmap_path))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        if not self.pixmap.isNull():
            scaled_pixmap = self.pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            point = rect.center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)


# Custom widget allows to control volume and hide volume slider when it's not needed
class VolumeWidget(QWidget):
    def __init__(self, mute_handler, volume_handler):
        super().__init__()

        # Volume/Mute button
        self.volume_icon = QIcon(resource_path('img/volume.png'))
        self.mute_icon = QIcon(resource_path('img/mute.png'))
        self.volume_button = QPushButton()
        self.volume_button.setIcon(self.volume_icon)
        self.volume_button.setIconSize(button_icon_size)
        self.volume_button.setFixedSize(self.volume_button.iconSize())
        self.volume_button.clicked.connect(mute_handler)

        # Volume slider
        self.volume_slider = VolumeSlider()
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.setFixedWidth(130)
        self.volume_slider.valueChanged.connect(volume_handler)
        self.volume_slider.hide()

        self.volume_layout = QHBoxLayout(self)
        self.volume_layout.setContentsMargins(0, 0, 0, 0)
        self.volume_layout.addWidget(self.volume_button)
        self.volume_layout.addWidget(self.volume_slider)

        self.volume_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.volume_slider.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if self.volume_button.isEnabled():
            if event.type() == QEvent.Enter:
                self.volume_slider.show()
            elif event.type() == QEvent.Leave:
                self.volume_slider.hide()
        return super(VolumeWidget, self).eventFilter(obj, event)


# app constants
app_name = 'Alex MultiMedia'
initial_volume = 15
button_icon_size = QSize(25, 25)
initial_dir = 'D:/My documents/Downloads'
file_filter = "Video and Music Files (*.mp4 *.avi *.mkv *.wmv *.mp3 *.flac *.m4a)"
default_album_cover_path = 'img/default_album_cover.jpg'


class MainWindow(QMainWindow):

    def __init__(self, file_path=None):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path('img/app_icon.ico')))
        self.setWindowTitle(app_name)
        self.setGeometry(320, 180, 960, 540)
        self.setStyleSheet("""
            * {
                background-color: black;
            }
            QLabel {
                font-size: 16px;
            }
            QPushButton {
                border: none;
            }
        """)
        # Window flags which allow this app's window to always stay on top of other windows
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.build_player()

        if file_path:
            self.play_file(file_path)

    def build_player(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.media_layout = QVBoxLayout(self.central_widget)
        self.media_layout.setContentsMargins(0, 0, 0, 0)
        # Widget to show output for video files
        self.video_widget = QVideoWidget()
        self.media_layout.addWidget(self.video_widget)
        # Label to show output (album cover image) for music files
        self.image_label = ImageLabel()
        self.media_layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.create_controls()
        self.enable_controls(False)
        self.create_shortcuts()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setVideoOutput(self.video_widget)

        # Timer to update the playback time label
        self.playback_time_timer = QTimer(self)
        self.playback_time_timer.setInterval(1000)  # update every second
        self.playback_time_timer.timeout.connect(self.update_time_label)
        self.playback_time_timer.start()

        # Timer to distinguish single and double clicks
        self.click_detection_timer = QTimer()
        self.click_detection_timer.setSingleShot(True)
        self.click_detection_timer.timeout.connect(self.single_click_handler)

        # Connect events
        self.mediaPlayer.stateChanged.connect(self.playing_state_handler)
        self.mediaPlayer.positionChanged.connect(self.position_handler)
        self.mediaPlayer.durationChanged.connect(self.duration_handler)

        self.previous_volume = initial_volume

        # Set player's initial volume
        self.mediaPlayer.setVolume(initial_volume)

    def create_controls(self):
        # Play/Pause button
        self.play_icon = QIcon(resource_path('img/play.png'))
        self.pause_icon = QIcon(resource_path('img/pause.png'))
        self.play_button = QPushButton()
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(button_icon_size)
        self.play_button.clicked.connect(self.play)

        # Replay 10 seconds button
        self.replay_10_button = QPushButton()
        self.replay_10_button.setIcon(QIcon(resource_path('img/replay10.png')))
        self.replay_10_button.setIconSize(button_icon_size)
        self.replay_10_button.clicked.connect(lambda: self.rewind_media(10500))

        # Forward 30 seconds button
        self.forward_30_button = QPushButton()
        self.forward_30_button.setIcon(QIcon(resource_path('img/forward30.png')))
        self.forward_30_button.setIconSize(button_icon_size)
        self.forward_30_button.clicked.connect(lambda: self.forward_media(30000))

        # Volume widget
        self.volume_widget = VolumeWidget(self.mute_handler, self.volume_handler)

        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)

        # Progress label
        self.progress_label = QLabel('0:00:00 / 0:00:00')

        # Open File button
        self.open_button = QPushButton()
        self.open_button.setIcon(QIcon(resource_path('img/openFile.png')))
        self.open_button.setIconSize(button_icon_size)
        self.open_button.clicked.connect(self.open_file)

        # Sets cursor to "pointer" for each control
        controls = [self.progress_slider, self.play_button, self.replay_10_button, self.forward_30_button,
                    self.volume_widget.volume_button, self.volume_widget.volume_slider, self.open_button]
        for control in controls:
            control.setCursor(Qt.CursorShape.PointingHandCursor)

        self.controls_bar = QWidget(self.central_widget)
        self.controls_bar.setStyleSheet("background-color: white;")

        self.controls_layout = QHBoxLayout(self.controls_bar)
        self.controls_layout.setContentsMargins(9, 0, 9, 0)
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.replay_10_button)
        self.controls_layout.addWidget(self.forward_30_button)
        self.controls_layout.addSpacing(2)
        self.controls_layout.addWidget(self.volume_widget)
        self.controls_layout.addSpacing(30)
        self.controls_layout.addWidget(self.progress_slider)
        self.controls_layout.addSpacing(5)
        self.controls_layout.addWidget(self.progress_label)
        self.controls_layout.addSpacing(5)
        self.controls_layout.addWidget(self.open_button)

    def create_shortcuts(self):
        # Play/Stop shortcut - 'Space'
        self.play_shortcut = QShortcut(Qt.Key_Space, self)
        self.play_shortcut.activated.connect(self.play)

        # Replay 1 minute shortcut - 'Arrow Left'
        self.replay_minute_shortcut = QShortcut(Qt.Key_Left, self)
        self.replay_minute_shortcut.activated.connect(lambda: self.rewind_media(60500))

        # Forward 1 minute shortcut - 'Arrow Right'
        self.forward_minute_shortcut = QShortcut(Qt.Key_Right, self)
        self.forward_minute_shortcut.activated.connect(lambda: self.forward_media(60000))

        # Hide Controls shortcut - 'Arrow Down'
        self.hide_controls_shortcut = QShortcut(Qt.Key_Down, self)
        self.hide_controls_shortcut.activated.connect(lambda: self.show_controls(False))
        # Show Controls shortcut - 'Arrow Up'
        self.show_controls_shortcut = QShortcut(Qt.Key_Up, self)
        self.show_controls_shortcut.activated.connect(lambda: self.show_controls(True))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', initial_dir, file_filter)
        self.play_file(file_path)

    def play_file(self, file_path):
        if file_path != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
            self.enable_controls(True)

            if file_path.endswith(('.mp3', '.m4a', '.flac')):
                self.image_label.show()
                self.video_widget.hide()
                self.display_album_cover(file_path)
            else:
                self.image_label.hide()
                self.video_widget.show()

            self.play()
            self.show_controls(False)
            self.setWindowTitle(f'{app_name} - {os.path.basename(file_path)}')

    def display_album_cover(self, file_path):
        if file_path.endswith('.mp3'):
            audio = MP3(file_path, ID3=ID3)
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    self.image_label.setPixmap(tag.data)
                    return
        elif file_path.endswith('.flac'):
            audio = FLAC(file_path)
            for picture in audio.pictures:
                self.image_label.setPixmap(picture.data)
                return
        elif file_path.endswith('.m4a'):
            audio = MP4(file_path)
            for cover in audio.tags.get('covr', []):
                if cover.imageformat == MP4Cover.FORMAT_JPEG or cover.imageformat == MP4Cover.FORMAT_PNG:
                    self.image_label.setPixmap(cover)
                    return
        self.image_label.setPixmapPath(resource_path(default_album_cover_path))

    def enable_controls(self, enabled):
        self.play_button.setEnabled(enabled)
        self.replay_10_button.setEnabled(enabled)
        self.forward_30_button.setEnabled(enabled)
        self.volume_widget.volume_button.setEnabled(enabled)
        self.progress_slider.setEnabled(enabled)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def playing_state_handler(self, state):
        if state == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.pause_icon)
        else:
            self.play_button.setIcon(self.play_icon)

    def position_handler(self, position):
        self.progress_slider.setValue(position)
        self.update_time_label()

    def duration_handler(self, duration):
        self.progress_slider.setRange(0, duration)

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def show_controls(self, show):
        if (show):
            self.controls_bar.show()
        else:
            self.controls_bar.hide()

    def update_time_label(self):
        current_time = self.mediaPlayer.position()
        total_time = self.mediaPlayer.duration()
        formatted_time = f'{self.format_time(current_time)} / {self.format_time(total_time)}'
        self.progress_label.setText(formatted_time)

    def format_time(self, ms):
        seconds = (ms / 1000) % 60
        minutes = (ms / (1000 * 60)) % 60
        hours = (ms / (1000 * 60 * 60)) % 24
        return "%01d:%02d:%02d" % (hours, minutes, seconds)

    # toggle between normal and full-screen mode
    def screen_mode_handler(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def mute_handler(self):
        if self.volume_widget.volume_slider.value() == 0:
            self.volume_widget.volume_slider.setValue(self.previous_volume)
        else:
            self.volume_widget.volume_slider.setValue(0)

    def volume_handler(self, value):
        if value == 0:
            self.volume_widget.volume_button.setIcon(self.volume_widget.mute_icon)
        else:
            self.volume_widget.volume_button.setIcon(self.volume_widget.volume_icon)
            self.previous_volume = value
        self.mediaPlayer.setVolume(value)

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

    # toggle between hidden and visible controls
    def single_click_handler(self):
        if not self.controls_bar.isVisible():
            self.show_controls(True)
        else:
            self.show_controls(False)

    # implementations of the parent methods ↓

    def mousePressEvent(self, event):
        # Starts the timer on mouse press
        if not self.click_detection_timer.isActive():
            self.click_detection_timer.start(200)  # 200 ms delay to differentiate single click from double click

    def mouseDoubleClickEvent(self, event):
        # Stops the single click timer if a double click is detected
        if self.click_detection_timer.isActive():
            self.click_detection_timer.stop()
        self.screen_mode_handler()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.screen_mode_handler()
        elif event.key() == Qt.Key_Escape and self.isFullScreen():
            self.showMaximized()

    def resizeEvent(self, event):
        self.controls_bar.setGeometry(15, self.height() - 55, self.width() - 30, 40)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # sys argument allows to open files with this desktop app
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    window = MainWindow(file_path)

    window.show()
    sys.exit(app.exec_())
