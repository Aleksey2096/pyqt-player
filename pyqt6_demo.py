import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QSlider, QLabel, QHBoxLayout
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QCloseEvent

class MediaPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt6 Media Player")

        # Initialize Media Player
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Video widget
        self.video_widget = QVideoWidget()
        self.player.setVideoOutput(self.video_widget)

        # UI Elements
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.open_button = QPushButton("Open File")
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)

        # Set up layout
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(QLabel("Volume"))
        control_layout.addWidget(self.volume_slider)

        layout = QVBoxLayout()
        layout.addWidget(self.video_widget)  # Add the video widget to the layout
        layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect signals and slots
        self.open_button.clicked.connect(self.open_file)
        self.play_button.clicked.connect(self.play_media)
        self.stop_button.clicked.connect(self.stop_media)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # Load playback positions
        self.app_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'PyQt6MediaPlayer')
        os.makedirs(self.app_data_dir, exist_ok=True)
        self.playback_file = os.path.join(self.app_data_dir, 'playback_state.json')
        self.playback_positions = self.load_playback_positions()

        # Initialize last file path
        self.current_file_path = None

    def open_file(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Open Media File")

        if file_path:
            self.current_file_path = file_path
            self.player.setSource(QUrl.fromLocalFile(file_path))
            
            # Resume playback if a position was saved
            if file_path in self.playback_positions:
                self.player.setPosition(self.playback_positions[file_path])

    def play_media(self):
        if self.current_file_path:
            self.player.play()

    def stop_media(self):
        if self.current_file_path:
            self.player.pause()
            self.save_playback_position()

    def set_volume(self, value):
        self.audio_output.setVolume(value / 100)

    def save_playback_position(self):
        if self.current_file_path:
            self.playback_positions[self.current_file_path] = self.player.position()
            with open(self.playback_file, 'w') as f:
                json.dump(self.playback_positions, f)

    def load_playback_positions(self):
        if os.path.exists(self.playback_file):
            with open(self.playback_file, 'r') as f:
                return json.load(f)
        return {}

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.current_file_path:
            self.save_playback_position()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())
