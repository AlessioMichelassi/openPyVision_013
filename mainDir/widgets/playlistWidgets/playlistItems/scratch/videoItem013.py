import json
import cv2
import subprocess

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import os
import tempfile

from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.baseItem import BaseItem


class VideoData:
    codec = {'avi': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'wmv1', 'wmv2', 'yuv4'],
             'mov': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'mp4': ['libx264', 'libx265', 'mpeg4'],
             'mkv': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'webm': ['libvpx', 'libvpx-vp9']}

    def __init__(self, filePath):
        self.filePath = filePath
        self.name = os.path.basename(filePath)
        self.temp_folder = os.path.join(tempfile.gettempdir(), self.name)
        self.video_info = {}
        self.audio_info = {}
        self.thumbnail = None

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        self.loadData()

    def loadData(self):
        saved_info_path = os.path.join(self.temp_folder, "video_info.json")
        if os.path.exists(saved_info_path):
            self.loadSavedVideoInfo(saved_info_path)
        else:
            self.extractVideoInfo()
            self.extractAudioInfo()
            self.thumbnail = self.getVideoThumbnail(self.filePath)
            self.saveVideoInfo()

    def saveVideoInfo(self):
        video_info = {
            'video_info': self.video_info,
            'audio_info': self.audio_info
        }
        with open(os.path.join(self.temp_folder, "video_info.json"), 'w') as f:
            json.dump(video_info, f)
        if self.thumbnail:
            self.thumbnail.save(os.path.join(self.temp_folder, "thumbnail.png"))

    def loadSavedVideoInfo(self, saved_info_path):
        with open(saved_info_path, 'r') as f:
            video_info = json.load(f)
        self.video_info = video_info['video_info']
        self.audio_info = video_info['audio_info']
        self.thumbnail = QPixmap(os.path.join(self.temp_folder, "thumbnail.png"))

    def extractVideoInfo(self):
        video_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=width,height,codec_name,avg_frame_rate,duration', '-of', 'default=noprint_wrappers=1', self.filePath
        ]
        video_info = subprocess.run(video_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if video_info.returncode == 0:
            self.video_info = self.parse_ffprobe_output(video_info.stdout)
            self.video_info['fps'] = int(
                eval(self.video_info.get('avg_frame_rate', '0/1'))) if '/' in self.video_info.get('avg_frame_rate',
                                                                                                  '0/1') else self.video_info.get(
                'avg_frame_rate')

    def extractAudioInfo(self):
        audio_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
            'stream=codec_name,sample_rate,channels,duration', '-of', 'default=noprint_wrappers=1', self.filePath
        ]
        audio_info = subprocess.run(audio_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if audio_info.returncode == 0:
            self.audio_info = self.parse_ffprobe_output(audio_info.stdout)
            duration = float(self.audio_info.get('duration', '0'))
            minutes, seconds = divmod(int(duration), 60)
            self.audio_info['duration_minutes'] = minutes
            self.audio_info['duration_seconds'] = seconds

    @staticmethod
    def parse_ffprobe_output(output):
        info_dict = {}
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=')
                info_dict[key.strip()] = value.strip()
        return info_dict

    @staticmethod
    def getVideoThumbnail(path):
        cap = cv2.VideoCapture(path)
        frame = None
        success = False
        for i in range(160):
            success, frame = cap.read()
            if not success:
                break
            if cv2.mean(frame)[:3] > (190, 190, 190):
                break
        cap.release()
        if success and frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
            return QPixmap.fromImage(q_image)
        return QPixmap()


class ItemVideo(BaseItem):
    def __init__(self, filePath=None, parent=None):
        super().__init__(parent)
        self.initConnections()
        self.name = ""
        self.path = ""
        self.video_data = None
        if filePath:
            self.loadVideoFile(filePath)

    def initConnections(self):
        super().initConnections()
        self.btnLoad.clicked.connect(self.loadItem)

    def loadItem(self):
        container_filters = []
        for container in VideoData.codec.keys():
            container_filters.append(f"*.{container}")
        all_containers_filter = f"Video Files ({' '.join(container_filters)})"
        all_files_filter = "All Files (*)"
        codec_filters = []
        for container, codecs in VideoData.codec.items():
            for codec in codecs:
                codec_filters.append(f"{codec.upper()} Files (*.{container})")

        file_filter = ";;".join([all_containers_filter, all_files_filter] + codec_filters)
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', file_filter)
        if filePath:
            self.loadVideoFile(filePath)

    def loadVideoFile(self, filePath):
        self.video_data = VideoData(filePath)
        self.name = self.video_data.name
        self.path = self.video_data.filePath

        self.setThumbnail(self.video_data.thumbnail)
        self.setFileName(self.name)
        self.setStartAt("00:00")
        self.update()
        self.updateVideoLabels(self.video_data.video_info)
        self.updateAudioLabels(self.video_data.audio_info)

    def updateVideoLabels(self, video_info_dict):
        video_codec = video_info_dict.get('codec_name', 'Unknown')
        width = video_info_dict.get('width', '0000')
        height = video_info_dict.get('height', '0000')
        fps = video_info_dict.get('fps', '0')
        duration = float(video_info_dict.get('duration', '0'))
        duration_minutes, duration_seconds = divmod(int(duration), 60)
        self.setMediaCodec(f"{video_codec}: {width}x{height}@{fps}fps")
        self.setEndAt(f"{duration_minutes:02}:{duration_seconds:02}")

    def updateAudioLabels(self, audio_info_dict):
        audio_codec = audio_info_dict.get('codec_name', 'Unknown')
        sample_rate = audio_info_dict.get('sample_rate', '0000')
        channels = int(audio_info_dict.get('channels', '0'))
        minutes = audio_info_dict.get('duration_minutes', 0)
        seconds = audio_info_dict.get('duration_seconds', 0)
        self.setAudioCodec(f"{audio_codec}: {sample_rate}Hz {channels}ch duration {minutes:02}:{seconds:02}")


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = ItemVideo()
    win.show()
    sys.exit(app.exec())
