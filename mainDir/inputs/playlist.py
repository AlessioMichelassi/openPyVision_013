import time
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from mainDir.inputs.baseClass import BaseClass
from mainDir.inputs.imageLoader_Still import ImageLoader
from mainDir.inputs.synchObject import SynchObject
from videoPlayer import VideoPlayerObject, VideoPlayerController


class PlaylistItem(BaseClass):
    """
    E' un input speciale che permette di riprodurre una lista di video o immagini in un determinato ordine
    ed è possibile stabilire il tempo di visualizzazione di ogni elemento o il punto di partenza o di fine
    in caso di video.
    E' anche possibile stabilire cosa deve succedere alla fine dell'elemento:
     - "cutToNext": taglia al prossimo elemento
     - "fadeToNext": fa un fade al prossimo elemento
     - "fadeToBlack": fa un fade al nero alla fine dell'elemento e poi taglia al prossimo elemento
     - "stop": si ferma e di conseguenza ferma la playlist
    E' possibile anche stabilire se l'elemento si deve ripetere e in che modo:
     - "loopForever": ripete all'infinito l'elemento
     - "loopNTimes": ripete l'elemento un numero di volte stabilito
     - "loopToNext": ripete l'elemento e poi taglia al prossimo elemento
    """

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.target_resolution = (resolution.height(), resolution.width())
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.playlist = []
        self.currentItem = -1
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_end)
        self.video_controller = None  # Controllo del video player

    def stop(self):
        super().stop()
        try:
            if self.currentItem != -1 and self.playlist[self.currentItem]["object"]:
                self.playlist[self.currentItem]["object"].stop()
            self.timer.stop()
            if self.video_controller:
                self.video_controller.stop()
        except Exception as e:
            print(f"Error stopping PlaylistItem: {e}")
            self._frame = np.zeros((self.target_resolution[0], self.target_resolution[1], 3), dtype=np.uint8)

    def captureFrame(self):
        if self.currentItem != -1 and self.currentItem < len(self.playlist):
            if isinstance(self.playlist[self.currentItem]["object"], VideoPlayerController):
                self.playlist[self.currentItem]["object"].video_player.captureFrame()
            self._frame = self.playlist[self.currentItem]["object"].getFrame()
        self.updateFps()

    def getFrame(self):
        return self._frame

    def loadPlaylist(self, playlist):
        self.currentItem = -1
        for item in playlist:
            obj = None
            if item["type"] == "video":
                vid = VideoPlayerObject(self.synch_Object, QSize(self.target_resolution[1], self.target_resolution[0]))
                vid.setMedia(item["path"])
                obj = VideoPlayerController(vid)
            elif item["type"] == "image":
                obj = ImageLoader(self.synch_Object, item["path"],
                                  QSize(self.target_resolution[1], self.target_resolution[0]))
            self.playlist.append({
                "object": obj,
                "duration": item["duration"],
                "startTime": None,
                "loop": item["loop"],
                "endAction": item["endAction"],
                "repeatsLeft": item.get("repeatsLeft", -1)  # -1 indicates infinite repeats
            })
        self.start_next_item()

    def start_next_item(self):
        if self.currentItem != -1 and self.playlist[self.currentItem]["object"]:
            self.playlist[self.currentItem]["object"].stop()
        self.currentItem += 1
        if self.currentItem < len(self.playlist):
            self.playlist[self.currentItem]["object"].play()
            if isinstance(self.playlist[self.currentItem]["object"], VideoPlayerController):
                self.video_controller = self.playlist[self.currentItem]["object"]
                self.video_controller.play()
            self.playlist[self.currentItem]["startTime"] = time.time()
            self.timer.start(1000 // 60)  # Check every frame (assuming 60 FPS)
        else:
            self.stop()

    def check_end(self):
        if self.currentItem != -1 and self.currentItem < len(self.playlist):
            current_item = self.playlist[self.currentItem]
            elapsed_time = time.time() - current_item["startTime"]
            if elapsed_time >= current_item["duration"]:
                self.handle_end_action(current_item)
        else:
            self.stop()

    def handle_end_action(self, item):
        if item["loop"] == "loopForever":
            item["object"].play()
            item["startTime"] = time.time()
        elif item["loop"] == "loopNTimes":
            if item["repeatsLeft"] > 0:
                item["repeatsLeft"] -= 1
                item["object"].play()
                item["startTime"] = time.time()
            else:
                self.execute_end_action(item)
        elif item["loop"] == "noLoop":
            self.execute_end_action(item)
        else:
            self.execute_end_action(item)

    def execute_end_action(self, item):
        if item["endAction"] == "cutToNext":
            self.start_next_item()
        elif item["endAction"] == "fadeToNext":
            # Implement fade to next logic here
            self.start_next_item()
        elif item["endAction"] == "fadeToBlack":
            # Implement fade to black logic here
            self.start_next_item()
        elif item["endAction"] == "stop":
            self.stop()


# Example usage
if __name__ == "__main__":
    import sys

    class PlaylistApp(QApplication):
        def __init__(self, argv):
            super().__init__(argv)
            self.synchObject = SynchObject(60)  # Set FPS to 60
            self.playlist_item = PlaylistItem(self.synchObject, resolution=QSize(1920, 1080))
            self.playlist_item.loadPlaylist([
                {"type": "video", "path": "C:/Users/aless/Videos/avt2.mp4", "duration": 1, "loop": "noLoop",
                 "endAction": "cutToNext"},
                {"type": "image", "path": "C:/Users/aless/Pictures/1920x1080p24_Color_Bars_blue.png", "duration": 1,
                 "loop": "noLoop", "endAction": "cutToNext"},
                {"type": "image", "path": "C:/Users/aless/Pictures/Grass_Valley_110_Switcher.jpg", "duration": 1,
                 "loop": "noLoop", "endAction": "cutToNext"},
            ])

            self.widget = QWidget()
            self.mainLayout = QVBoxLayout()
            self.viewer = QLabel()
            self.fpsLabel = QLabel()
            self.displayLabel = QLabel()
            self.mainLayout.addWidget(self.viewer)
            self.mainLayout.addWidget(self.fpsLabel)
            self.mainLayout.addWidget(self.displayLabel)
            self.widget.setLayout(self.mainLayout)
            self.widget.show()
            self.viewer.setFixedSize(1920, 1080)
            self.uiTimer = QTimer(self)
            self.uiTimer.timeout.connect(self.display_frame)
            self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS

        def display_frame(self):
            self.playlist_item.captureFrame()
            frame = self.playlist_item.getFrame()
            if frame is not None and frame.size != 0:
                start_time = time.time()
                image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
                self.viewer.setPixmap(QPixmap.fromImage(image))
                display_time = time.time() - start_time
                self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
                self.fpsLabel.setText(f"FPS: {self.playlist_item.fps:.2f}")

    def main():
        app = PlaylistApp(sys.argv)
        app.exec()

    if __name__ == '__main__':
        main()
