import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QPushButton, QStyle, QHBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Volume Controller Example")
        self.setGeometry(100, 100, 800, 600)

        # Set up the media player
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        
        # Create video widget
        self.videoWidget = QVideoWidget()
        
        # Create play button
        self.playButton = QPushButton()
        self.playButton.setEnabled(True)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play_video)

        # Create volume slider
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 200)  # Set max volume to 200
        self.volumeSlider.setValue(100)  # Default value at 100
        self.volumeSlider.valueChanged.connect(self.set_volume)

        # Create a label to show volume value
        self.volumeLabel = QLabel("Volume: 100")
        
        # Create layout for controls
        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.volumeSlider)
        controlLayout.addWidget(self.volumeLabel)

        # Create main layout
        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)

        # Set the central widget
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        # Set the media player output to the video widget
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Set a video source
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile('D://My documents//Downloads//American.Pie.1999.1080p.BluRay.x264-[YTS.AG].mp4')))

    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.mediaPlayer.play()
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_volume(self, value):
        self.mediaPlayer.setVolume(value)
        self.volumeLabel.setText(f"Volume: {value}")
        print(f"Volume changed to: {value}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
