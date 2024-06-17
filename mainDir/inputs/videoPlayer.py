import os
import subprocess
import time
import wave

import cv2
import numpy as np
import pyaudio
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.inputs.baseClass import BaseClass
from mainDir.inputs.synchObject import SynchObject


class VideoPlayerObject(BaseClass):
    tempFolder = r"temp"

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self.videoCapture = None
        self.audio_file = None
        self.wf = None
        self.p = None
        self.stream = None
        self.time = QTime()

    def __del__(self):
        self.stop()

    def setMedia(self, media):
        self.videoCapture = cv2.VideoCapture(media)
        if not self.videoCapture.isOpened():
            raise ValueError("Video file could not be opened")
        fileName = os.path.basename(media)
        fileName = fileName.replace(".mov", ".wav").replace(".mp4", ".wav")
        if not os.path.exists(self.tempFolder):
            os.makedirs(self.tempFolder)
        self.audio_file = os.path.join(self.tempFolder, fileName)
        if not os.path.exists(self.audio_file):
            _ = self.extractAudio(media)

    def play(self):
        self.initAudioDevice()
        self.realFrameRate = self.videoCapture.get(cv2.CAP_PROP_FPS)
        self.time.start()
        self.stream.start_stream()

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()
        if self.wf:
            self.wf.close()
        if self.videoCapture:
            self.videoCapture.release()
        try:
            os.remove(self.audio_file)
            if hasattr(self, 'frame_processor') and self.frame_processor and self.frame_processor.isRunning():
                self.frame_processor.stop()
        except Exception as e:
            pass

    def initAudioDevice(self):
        self.wf = wave.open(self.audio_file, 'rb')
        self.p = pyaudio.PyAudio()

        def callback(in_data, frame_count, time_info, status):
            data = self.wf.readframes(frame_count)
            return data, pyaudio.paContinue

        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  output=True,
                                  stream_callback=callback)

    def extractAudio(self, input_video_path):
        command = [
            'ffmpeg',
            '-i', input_video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            self.audio_file
        ]
        try:
            subprocess.run(command, check=True, stderr=subprocess.PIPE)
            print(f"Audio estratto con successo e salvato in: {self.audio_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'estrazione dell'audio: {e}")
            return False

    def next_frame(self):
        elapsed_time = self.time.elapsed()
        expected_frame = int(elapsed_time * self.realFrameRate / 1000.0)
        current_frame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
        while current_frame < expected_frame and self.videoCapture.isOpened():
            ret, frame = self.videoCapture.read()
            if ret:
                if frame.shape[1] != self.resolution.width():
                    self._frame = cv2.resize(frame, (self.resolution.width(), self.resolution.height()))
                else:
                    self._frame = frame
                current_frame += 1
            else:
                self.stop()

    def capture_frame(self):
        self.update_fps()

    def getFrame(self):
        return self._frame


class VideoPlayerController(QObject):
    def __init__(self, video_player):
        super().__init__()
        self.video_player = video_player
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.video_player.next_frame)

    def play(self):
        self.video_player.play()
        self.timer.start(int(1000 // self.video_player.realFrameRate))

    def stop(self):
        self.timer.stop()
        self.video_player.stop()


# Example usage of the VideoPlayerObject class

if __name__ == "__main__":
    import sys
    import time

    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *

    from mainDir.inputs.synchObject import SynchObject

    class VideoApp(QApplication):
        def __init__(self, argv):
            super().__init__(argv)
            self.synchObject = SynchObject(60)  # Set FPS to 60
            self.input1 = VideoPlayerObject(self.synchObject, resolution=QSize(1920, 1080))
            self.input1.setMedia(r"C:\Users\aless\Videos\avt2.mp4")  # Set the path to your video file
            self.controller = VideoPlayerController(self.input1)
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
            QTimer.singleShot(10000, self.stop_app)
            self.controller.play()

        def display_frame(self):
            frame = self.input1.getFrame()
            if frame is not None and frame.size != 0:
                start_time = time.time()
                image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
                self.viewer.setPixmap(QPixmap.fromImage(image))
                display_time = time.time() - start_time
                self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
                self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")

        def stop_app(self):
            print(f"Media FPS: {self.input1.fps:.2f}")
            self.controller.stop()
            self.exit()

    def main():
        app = VideoApp(sys.argv)
        app.exec()

    if __name__ == '__main__':
        import cProfile
        import pstats
        import io

        pr = cProfile.Profile()
        pr.enable()
        main()
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
