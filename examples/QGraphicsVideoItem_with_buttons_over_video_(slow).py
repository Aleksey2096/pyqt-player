"""

QMainWindow
    QWidget = central_widget
        QVBoxLayout = media_layout
            QVideoWidget = video_widget
            ImageLabel = image_label
        QWidget = controls_container
            QHBoxLayout = controls_layout
                ... various controls
        QPushButton = openBtn

"""
import sys
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsWidget, QVBoxLayout, QPushButton, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl, QSizeF
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Set the attribute for a translucent background
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Apply a transparent background color
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        # Create a layout and add some buttons for demonstration
        layout = QVBoxLayout()
        layout.addWidget(QPushButton("Button 1"))
        layout.addWidget(QPushButton("Button 2"))
        layout.addWidget(QPushButton("Button 3"))

        # Set the layout for the widget
        self.setLayout(layout)

class VideoPlayer(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Create a scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Create a QGraphicsVideoItem and add it to the scene
        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)

        # Create a media player and set the video output to the video item
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_item)

        # Load a video file
        self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile('D:/My documents/Downloads/American.Pie.1999.1080p.BluRay.x264-[YTS.AG].mp4')))
        self.media_player.play()

        # Create the transparent overlay widget
        self.overlay_widget = TransparentOverlay()

        # Add the overlay widget to the scene
        self.overlay_item = self.scene.addWidget(self.overlay_widget)

        # Set the scene rectangle to the size of the video item
        self.setSceneRect(self.video_item.boundingRect())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize the scene rectangle when the view is resized
        self.setSceneRect(0, 0, self.width(), self.height())
        self.video_item.setSize(QSizeF(self.size()))
        self.overlay_item.setGeometry(self.sceneRect())

app = QApplication(sys.argv)
player = VideoPlayer()
player.resize(800, 600)
player.show()
sys.exit(app.exec_())
