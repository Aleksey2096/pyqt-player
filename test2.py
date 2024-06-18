import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QWidget,QSizePolicy
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        self.setGeometry(100, 100, 300, 300)

        # Central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Video Widget
        self.video_widget = QVideoWidget(self)
        self.layout.addWidget(self.video_widget)
        
        # Image Label
        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.image_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # self.image_label.setScaledContents(True)  # This allows the label to scale the pixmap
        
        # Media Player
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

        # Show File Dialog to open file
        self.open_file_dialog()

    def open_file_dialog(self):
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptOpen)
        file_dialog.setNameFilter("Media Files (*.mp4 *.mp3 *.avi *.mkv)")
        if file_dialog.exec_() == QFileDialog.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            self.load_media(file_path)

    def load_media(self, file_path):
        if file_path.endswith('.mp3'):
            self.display_album_cover(file_path)
        else:
            self.play_video(file_path)

    def play_video(self, file_path):
        self.image_label.hide()
        self.video_widget.show()
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.media_player.play()

    def display_album_cover(self, file_path):
        audio = MP3(file_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                pixmap = QPixmap()
                pixmap.loadFromData(tag.data)
                self.image_label.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.image_label.show()
                self.video_widget.hide()
                self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
                self.media_player.play()
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
