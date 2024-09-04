import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QSlider, QLabel, QHBoxLayout, QGridLayout
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QPalette, QColor

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

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.sliderMoved.connect(self.seek_position)

        # Set up layout for controls
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.open_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(QLabel("Volume"))
        control_layout.addWidget(self.volume_slider)

        controls_widget = QWidget()
        controls_widget.setLayout(control_layout)

        # Optional: Set the background of controls to be semi-transparent
        palette = controls_widget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0, 150))  # Semi-transparent black
        controls_widget.setAutoFillBackground(True)
        controls_widget.setPalette(palette)

        # Create a layout to overlay the video and controls
        overlay_layout = QGridLayout()
        overlay_layout.addWidget(self.video_widget, 0, 0)
        overlay_layout.addWidget(self.progress_slider, 1, 0)
        overlay_layout.addWidget(controls_widget, 2, 0)
        overlay_layout.setRowStretch(0, 5)
        overlay_layout.setRowStretch(1, 1)
        overlay_layout.setRowStretch(2, 1)
        overlay_layout.setAlignment(controls_widget, Qt.AlignmentFlag.AlignBottom)

        container = QWidget()
        container.setLayout(overlay_layout)
        self.setCentralWidget(container)

        # Connect signals and slots
        self.open_button.clicked.connect(self.open_file)
        self.play_button.clicked.connect(self.play_media)
        self.stop_button.clicked.connect(self.stop_media)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.player.positionChanged.connect(self.update_position)
        self.player.durationChanged.connect(self.update_duration)

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

    def update_position(self, position):
        if self.player.duration() > 0:
            self.progress_slider.setValue(position)

    def update_duration(self, duration):
        self.progress_slider.setRange(0, duration)

    def seek_position(self, position):
        self.player.setPosition(position)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MediaPlayer()
    player.show()
    sys.exit(app.exec())
