import json
import cv2
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import tempfile
import os
import numpy as np
import soundfile as sf

from mainDir.widgets.playlistWidgets.playlistItems.audioThreadCalculator import VolumeCalculator
from mainDir.widgets.playlistWidgets.playlistItems.baseItem import BaseItem


class ItemVideo(BaseItem):
    available_codecs = []
    codec = {'avi': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'wmv1', 'wmv2', 'yuv4'],
             'mov': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'mp4': ['libx264', 'libx265', 'mpeg4'],
             'mkv': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'webm': ['libvpx', 'libvpx-vp9']}

    def __init__(self, filePath=None, parent=None):
        super().__init__(parent)
        self.initConnections()
        if filePath:
            self.loadVideoFile(filePath)

    def initConnections(self):
        super().initConnections()
        self.btnLoad.clicked.connect(self.loadItem)

    def loadItem(self):
        """
        Open a file dialog to select a video file
        :return:
        """
        container_filters = []
        for container in self.codec.keys():
            container_filters.append(f"*.{container}")
        all_containers_filter = f"Video Files ({' '.join(container_filters)})"
        all_files_filter = "All Files (*)"
        codec_filters = []
        for container, codecs in self.codec.items():
            for codec in codecs:
                codec_filters.append(f"{codec.upper()} Files (*.{container})")

        file_filter = ";;".join([all_containers_filter, all_files_filter] + codec_filters)
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', file_filter)
        if filePath:
            self.loadVideoFile(filePath)

    def loadVideoFile(self, filePath):
        """
        Load the video file and update the UI
        :param filePath: Path to the video file
        """
        self.name = filePath.split('/')[-1]
        self.path = filePath
        self.setThumbnail(self.getVideoThumbnail(filePath))
        self.setFileName(self.name)
        self.setStartAt("00:00")
        self.update()
        self.getVideoInfo(filePath)

    def getVideoInfo(self, path):
        """
        Main function to get video information, update labels, and check for black frames.
        :param path: Path to the video file
        """
        video_info_dict = self.extractVideoInfo(path)
        self.updateVideoLabels(video_info_dict)

        audio_info_dict = self.extractAudioInfo(path)
        self.updateAudioLabels(audio_info_dict)

        self.checkBlackFrames(path, video_info_dict.get('fps', 30), audio_info_dict.get('duration_seconds', 0),
                              audio_info_dict.get('duration_minutes', 0))

    def extractVideoInfo(self, path):
        """
        Extracts video information using ffprobe.
        :param path: Path to the video file
        :return: Dictionary with video information
        """
        video_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=width,height,codec_name,avg_frame_rate,duration', '-of', 'default=noprint_wrappers=1', path
        ]
        video_info = subprocess.run(video_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if video_info.returncode == 0:
            video_info_dict = self.parse_ffprobe_output(video_info.stdout)
            video_info_dict['fps'] = int(
                eval(video_info_dict.get('avg_frame_rate', '0/1'))) if '/' in video_info_dict.get('avg_frame_rate',
                                                                                                  '0/1') else video_info_dict.get(
                'avg_frame_rate')
            return video_info_dict
        return {}

    def extractAudioInfo(self, path):
        """
        Extracts audio information using ffprobe.
        :param path: Path to the video file
        :return: Dictionary with audio information
        """
        audio_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
            'stream=codec_name,sample_rate,channels,duration', '-of', 'default=noprint_wrappers=1', path
        ]
        audio_info = subprocess.run(audio_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if audio_info.returncode == 0:
            audio_info_dict = self.parse_ffprobe_output(audio_info.stdout)
            duration = float(audio_info_dict.get('duration', '0'))
            minutes, seconds = divmod(int(duration), 60)
            audio_info_dict['duration_minutes'] = minutes
            audio_info_dict['duration_seconds'] = seconds
            self.volumeCalculator = VolumeCalculator(path)
            self.volumeCalculator.volumeCalculated.connect(self.updateVolumeInfo)
            self.volumeCalculator.start()
            return audio_info_dict
        return {}

    def updateVideoLabels(self, video_info_dict):
        """
        Updates the UI labels with video information.
        :param video_info_dict: Dictionary with video information
        """
        video_codec = video_info_dict.get('codec_name', 'Unknown')
        width = video_info_dict.get('width', '0000')
        height = video_info_dict.get('height', '0000')
        fps = video_info_dict.get('fps', '0')
        duration = float(video_info_dict.get('duration', '0'))
        duration_minutes, duration_seconds = divmod(int(duration), 60)
        self.setMediaCodec(f"{video_codec}: {width}x{height}@{fps}fps")
        self.setEndAt(f"{duration_minutes:02}:{duration_seconds:02}")

    def updateAudioLabels(self, audio_info_dict):
        """
        Updates the UI labels with audio information.
        :param audio_info_dict: Dictionary with audio information
        """
        audio_codec = audio_info_dict.get('codec_name', 'Unknown')
        sample_rate = audio_info_dict.get('sample_rate', '0000')
        channels = int(audio_info_dict.get('channels', '0'))
        minutes = audio_info_dict.get('duration_minutes', 0)
        seconds = audio_info_dict.get('duration_seconds', 0)
        self.setAudioCodec(f"{audio_codec}: {sample_rate}Hz {channels}ch duration {minutes:02}:{seconds:02}")

    def checkBlackFrames(self, path, fps, duration_seconds, duration_minutes):
        """
        Checks for black frames at the start and end of the video.
        :param path: Path to the video file
        :param fps: Frames per second of the video
        :param duration_seconds: Total seconds duration of the video
        :param duration_minutes: Total minutes duration of the video
        """
        start_black_frame = self.check_black_frame(path, start=True)
        end_black_frame = self.check_black_frame(path, start=False, fps=fps, duration_seconds=duration_seconds,
                                                 duration_minutes=duration_minutes)
        if start_black_frame:
            self.setBlackFrameOnStart(f"- black frame at start - first frame {start_black_frame}")
        if end_black_frame:
            self.setBlackFrameOnEnd(f"- black frame start at {end_black_frame} from end")
        else:
            self.setBlackFrameOnEnd("- no black frame at end")

    def updateVolumeInfo(self, avg_volumes):
        avg_volume_str = ', '.join([f"Ch{idx + 1}: {vol:.2f}dB" for idx, vol in enumerate(avg_volumes) if vol is not None])
        self.setVolume(f"Avg Vol: {avg_volume_str}")

    def check_black_frame(self, path, start=True, fps=30, duration_seconds=0, duration_minutes=0):
        cap = cv2.VideoCapture(path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_number = 0 if start else total_frames - 1
        increment = 1 if start else -1

        for _ in range(160):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = cap.read()
            if not success:
                break
            if cv2.mean(frame)[:3] > (18, 18, 18):
                cap.release()
                if start:
                    return frame_number
                else:
                    frames_from_end = total_frames - frame_number
                    seconds_from_end = frames_from_end / fps
                    minutes_from_end = int(seconds_from_end // 60)
                    seconds_from_end = int(seconds_from_end % 60)
                    return f"{minutes_from_end:02}:{seconds_from_end:02}"
            frame_number += increment

        cap.release()
        return None

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
                print('Error: Unable to capture video.')
                break
            if cv2.mean(frame)[:3] > (190, 190, 190):
                print(cv2.mean(frame)[:3])
                print(i)
                print('Frame found')
                break
        cap.release()

        if success and frame is not None:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).rgbSwapped()
            return QPixmap.fromImage(q_image)
        return QPixmap()


if __name__ == '__main__':
    app = QApplication([])
    widget = ItemVideo(r"C:\Users\aless\Videos\big_buck_bunny_1080p_h264.mov")
    widget.show()
    app.exec()
