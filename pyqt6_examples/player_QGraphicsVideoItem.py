import sys
import os
from PyQt6.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QHBoxLayout, QVBoxLayout, QPushButton,
                             QWidget, QSlider, QLabel, QFileDialog)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt, QSize, QSizeF
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
initial_volume = 15
button_icon_size = QSize(25, 25)
initial_dir = 'D:/My documents/Downloads'
file_filter = "Video and Music Files (*.mp4 *.avi *.mkv *.wmv *.mp3 *.flac *.m4a)"
default_album_cover_path = 'img/default_album_cover.jpg'


class ControlsBar(QWidget):
    def __init__(self):
        super().__init__()

        # Applies a transparent background color
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.create_controls()

        # Creates a layout and adds controls
        self.controls_layout = QHBoxLayout()
        self.controls_layout.addWidget(self.play_button)
        self.controls_layout.addWidget(self.replay_10_button)
        self.controls_layout.addWidget(self.forward_30_button)
        self.controls_layout.addWidget(self.volume_button)
        self.controls_layout.addWidget(self.volume_slider)
        self.controls_layout.addStretch()
        self.controls_layout.addWidget(self.progress_label)
        self.controls_layout.addWidget(self.open_button)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.progress_slider)
        self.main_layout.addLayout(self.controls_layout)

        # Sets the layout for the widget
        self.setLayout(self.main_layout)

    def create_controls(self):
        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)

        # Play/Pause button
        self.play_icon = QIcon(resource_path('img/play.png'))
        self.pause_icon = QIcon(resource_path('img/pause.png'))
        self.play_button = QPushButton()
        self.play_button.setIcon(self.play_icon)
        self.play_button.setIconSize(button_icon_size)

        # Replay 10 seconds button
        self.replay_10_button = QPushButton()
        self.replay_10_button.setIcon(QIcon(resource_path('img/replay10.png')))
        self.replay_10_button.setIconSize(button_icon_size)

        # Forward 30 seconds button
        self.forward_30_button = QPushButton()
        self.forward_30_button.setIcon(QIcon(resource_path('img/forward30.png')))
        self.forward_30_button.setIconSize(button_icon_size)

        # Volume/Mute button
        self.volume_icon = QIcon(resource_path('img/volume.png'))
        self.mute_icon = QIcon(resource_path('img/mute.png'))
        self.volume_button = QPushButton()
        self.volume_button.setIcon(self.volume_icon)
        self.volume_button.setIconSize(button_icon_size)

        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.setMaximumWidth(130)

        # Progress label
        self.progress_label = QLabel('0:00:00 / 0:00:00')

        # Open File button
        self.open_button = QPushButton()
        self.open_button.setIcon(QIcon(resource_path('img/openFile.png')))
        self.open_button.setIconSize(button_icon_size)

        # Sets cursor to "pointer" for each control
        controls = [self.progress_slider, self.play_button, self.replay_10_button,
                    self.forward_30_button, self.volume_button, self.volume_slider, self.open_button]
        for control in controls:
            control.setCursor(Qt.CursorShape.PointingHandCursor)


class MediaPlayer(QGraphicsView):
    def __init__(self, file_path=None):
        super().__init__()

        self.setWindowIcon(QIcon(resource_path('img/app_icon.ico')))
        self.setWindowTitle(app_name)
        self.setGeometry(320, 180, 960, 540)
        # Removes white border around QGraphicsView (main window)
        self.setFrameStyle(0)
        # Window flags which allow this app's window to always stay on top of other windows
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)  

        self.build_player()      

        if file_path:
            self.play_file(file_path)

    def build_player(self):
        # Creates a scene to hold the video item
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Creates a QGraphicsVideoItem and adds it to the scene
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        # Creates a ControlsBar and adds it to the scene
        self.controls_bar = ControlsBar()
        self.scene.addWidget(self.controls_bar)

        self.connectEvents()

        # Creates a media player and audio output and sets the video and audio outputs
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_item)

        self.media_player.errorOccurred.connect(self.handle_media_error)

        # Disables scrollbars (during resizing)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 

    def handle_media_error(self, error):
        print(f"Error: {error}")

    def connectEvents(self):



        self.controls_bar.open_button.clicked.connect(self.open_file)       

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open File', initial_dir, file_filter)

        self.play_file(file_path)

    def play_file(self, file_path):
        if file_path != '':


            # Step 1: Stop the media player
            self.media_player.stop()
            print('1')  
            # Step 2: Clear the current media source (to release resources)
            self.media_player.setSource(QUrl())  # Empty QUrl to clear source
            print('2')  
            # Step 3: Remove the video item from the scene to free resources
            self.scene.removeItem(self.video_item)
            self.video_item = None
            print('3')  
            # Step 4: Recreate the video item and add it back to the scene
            self.video_item = QGraphicsVideoItem()
            self.scene.addItem(self.video_item)
            print('4')      
            # Step 5: Set the media player to output to the new video item
            self.media_player.setVideoOutput(self.video_item)
            print('5')  

            self.current_file_path = file_path
            print('6')
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            print('7')
            self.media_player.play()
            print('8')
            self.setWindowTitle(f'{app_name} - {os.path.basename(file_path)}')
            print('9')

    # implementations of the parent methods ↓

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resizes video item to fit the view
        self.setSceneRect(0, 0, self.width(), self.height())
        self.video_item.setSize(QSizeF(self.size()))
        # Resizes ControlsBar to stay at the bottom of the screen
        self.controls_bar.setGeometry(20, self.height() - 90, self.width() - 40, 60)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Sets the global stylesheet
    app.setStyleSheet("""
        * { 
            background-color: black;
        }
        QLabel {
            font-size: 16px;
            color: white;
        }
    """)

    # sys argument allows to open files with this desktop app
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    player = MediaPlayer(file_path)

    player.show()
    sys.exit(app.exec())
