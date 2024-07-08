import json
import cv2
import subprocess
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import tempfile
import os
import wave
import numpy as np
import soundfile as sf


class VolumeCalculator(QThread):
    volumeCalculated = pyqtSignal(list)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        avg_volumes = []
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_wav_path = os.path.join(temp_dir, "audio.wav")
            cmd = [
                'ffmpeg', '-i', self.path, '-vn', '-ac', '2', '-ar', '44100',
                '-y', temp_wav_path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print(f"Running command: {' '.join(cmd)}")
            print(f"ffmpeg output: {result.stdout}")
            print(f"ffmpeg errors: {result.stderr}")

            if os.path.exists(temp_wav_path):
                avg_volumes = self.calculate_average_volume_from_wav(temp_wav_path)
            else:
                print(f"Error: File {temp_wav_path} was not created.")
        self.volumeCalculated.emit(avg_volumes)

    @staticmethod
    def calculate_average_volume_from_wav(wav_path, threshold=0.2):
        data, samplerate = sf.read(wav_path)
        channels = data.shape[1] if len(data.shape) > 1 else 1
        avg_volumes = []
        for ch in range(channels):
            samples = data[:, ch] if channels > 1 else data
            samples = np.abs(samples)
            samples = samples[samples > threshold]  # Ignore low-volume parts
            avg_volume = 20 * np.log10(np.mean(samples)) if samples.size > 0 else -np.inf
            avg_volumes.append(avg_volume)
        return avg_volumes


class ItemVideo(QWidget):
    available_codecs = []
    codec = {'avi': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'wmv1', 'wmv2', 'yuv4'],
             'mov': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'mp4': ['libx264', 'libx265', 'mpeg4'],
             'mkv': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'webm': ['libvpx', 'libvpx-vp9']}

    def __init__(self, item_type, name, path, transition='cutToNext', duration=None, option=''):
        super().__init__()
        self.item_type = item_type
        self.name = name
        self.path = path
        self.transition = transition
        self.duration = duration
        self.option = option

        # init widget
        self.lblThumbnail = QLabel()
        self.lblNiceName = QLabel(self.name)
        self.lblVideoCodec = QLabel('h26x: 0000x0000@000fps')
        self.lblAudioCodec = QLabel('Audio: 0000Hz 000ch duration 00:00')
        self.lblBlackOnStart = QLabel('Black On Start')
        self.lblBlackOnEnd = QLabel('Black On End')
        self.btnLoad = QPushButton('Load')
        self.btnEdit = QPushButton('Edit')
        self.cmbTransition = QComboBox()
        self.lneStartAt = QLineEdit()
        self.lneEndAt = QLineEdit()

        # init codec available
        self.initCodecAvailable()
        # init UI
        self.initUI()
        self.initStyles()
        self.populateWidget()
        self.initConnections()

    def initUI(self):
        mainLayout = QHBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(self.lblThumbnail)

        audioLayout = QVBoxLayout()
        audioLayout.addWidget(self.lblVideoCodec)
        audioLayout.addWidget(self.lblNiceName)
        audioLayout.addWidget(self.lblAudioCodec)
        audioLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(audioLayout)

        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnLoad)
        btnLayout.addWidget(self.btnEdit)
        btnLayout.addWidget(self.cmbTransition)

        lblStartAt = QLabel('Start at')
        btnLayout.addWidget(lblStartAt)
        btnLayout.addWidget(self.lneStartAt)

        lblEndAt = QLabel('End at')
        btnLayout.addWidget(lblEndAt)
        btnLayout.addWidget(self.lneEndAt)

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        btnLayout.addItem(spacer)

        mainLayout.addLayout(btnLayout)
        mainLayout.setSpacing(5)
        mainLayout.setContentsMargins(5, 5, 5, 5)

    def initConnections(self):
        self.btnLoad.clicked.connect(self.loadItem)
        self.btnEdit.clicked.connect(self.editItem)

    def initStyles(self):
        self.btnEdit.setMaximumWidth(50)
        self.btnLoad.setMaximumWidth(50)
        self.lblThumbnail.setFixedSize(64, 54)
        self.lblThumbnail.setScaledContents(True)
        self.lblThumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lblThumbnail.setStyleSheet("border: 1px solid black")
        self.lblNiceName.setFixedWidth(200)
        self.cmbTransition.setFixedWidth(100)
        self.lneStartAt.setFixedWidth(50)
        self.lneEndAt.setFixedWidth(50)
        self.lneStartAt.setPlaceholderText('00:00')
        self.lneEndAt.setPlaceholderText('00:00')

    def populateWidget(self):
        self.cmbTransition.addItems(
            ["cutToNext", "fadeToNext", "stop", "cutToBlack", "fadeToBlack", "loopForever", "loopForN"])
        self.cmbTransition.setCurrentText(self.transition)

    def setThumbnail(self, thumbnail):
        self.lblThumbnail.setPixmap(thumbnail.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio))

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
            self.name = filePath.split('/')[-1]
            self.path = filePath
            self.setThumbnail(self.getVideoThumbnail(filePath))
            self.lblNiceName.setText(self.name)
            self.lneStartAt.setText("00:00")
            self.update()
            self.getVideoInfo(filePath)

    def getVideoInfo(self, path):
        """
        Uses ffprobe to get video information
        :param path: Path to the video file
        """
        video_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'stream=width,height,codec_name,avg_frame_rate,duration', '-of', 'default=noprint_wrappers=1', path
        ]
        video_info = subprocess.run(video_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if video_info.returncode == 0:
            video_info_dict = self.parse_ffprobe_output(video_info.stdout)
            video_codec = video_info_dict.get('codec_name', 'Unknown')
            width = video_info_dict.get('width', '0000')
            height = video_info_dict.get('height', '0000')
            avg_frame_rate = video_info_dict.get('avg_frame_rate', '0/1')
            fps = int(eval(avg_frame_rate)) if '/' in avg_frame_rate else avg_frame_rate
            duration = float(video_info_dict.get('duration', '0'))
            duration_minutes, duration_seconds = divmod(int(duration), 60)
            self.lblVideoCodec.setText(f"{video_codec}: {width}x{height}@{fps}fps")
            self.lneEndAt.setText(f"{duration_minutes:02}:{duration_seconds:02}")

        audio_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
            'stream=codec_name,sample_rate,channels,duration', '-of', 'default=noprint_wrappers=1', path
        ]
        audio_info = subprocess.run(audio_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if audio_info.returncode == 0:
            audio_info_dict = self.parse_ffprobe_output(audio_info.stdout)
            audio_codec = audio_info_dict.get('codec_name', 'Unknown')
            sample_rate = audio_info_dict.get('sample_rate', '0000')
            channels = int(audio_info_dict.get('channels', '0'))
            duration = float(audio_info_dict.get('duration', '0'))
            minutes, seconds = divmod(int(duration), 60)
            self.lblAudioCodec.setText(f"{audio_codec}: {sample_rate}Hz {channels}ch duration {minutes:02}:{seconds:02}")

            # Start the volume calculation in a separate thread
            self.volumeCalculator = VolumeCalculator(path)
            self.volumeCalculator.volumeCalculated.connect(self.updateVolumeInfo)
            self.volumeCalculator.start()

        # Check for black frames at start and end
        start_black_frame = self.check_black_frame(path, start=True)
        end_black_frame = self.check_black_frame(path, start=False, fps=fps, duration_seconds=duration_seconds,
                                                 duration_minutes=duration_minutes)
        if start_black_frame:
            self.lblVideoCodec.setText(
                f"{self.lblVideoCodec.text()} - black frame at start - first frame {start_black_frame}")
        if end_black_frame:
            self.lblVideoCodec.setText(f"{self.lblVideoCodec.text()} - black frame start at {end_black_frame} from end")
        else:
            self.lblAudioCodec.setText(f"{self.lblAudioCodec.text()} - no black frame at end")

    def updateVolumeInfo(self, avg_volumes):
        avg_volume_str = ', '.join(
            [f"Ch{idx + 1}: {vol:.2f}dB" for idx, vol in enumerate(avg_volumes) if vol is not None])
        self.lblAudioCodec.setText(f"{self.lblAudioCodec.text()} - Avg Vol: {avg_volume_str}")

    def check_black_frame(self, path, start=True, fps=30, duration_seconds=0, duration_minutes=0):
        """
        Check for black frame at the start or end of the video
        :param path: Path to the video file
        :param start: If True, check at the start; if False, check at the end
        :param fps: Frames per second of the video
        :param duration_seconds: Total seconds duration of the video
        :param duration_minutes: Total minutes duration of the video
        :return: Frame number or time from end as a string
        """
        cap = cv2.VideoCapture(path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_number = 0 if start else total_frames - 1
        increment = 1 if start else -1

        for _ in range(160):  # Check up to 160 frames
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = cap.read()
            if not success:
                break
            if cv2.mean(frame)[:3] > (18, 18, 18):  # Use a threshold to check if the frame is not black
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
        """
        Parses ffprobe output into a dictionary
        :param output: ffprobe output
        :return: Dictionary with ffprobe information
        """
        info_dict = {}
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=')
                info_dict[key.strip()] = value.strip()
        return info_dict

    def editItem(self):
        pass

    @staticmethod
    def getVideoThumbnail(path):
        cap = cv2.VideoCapture(path)
        frame = None
        success = False

        for i in range(160):  # Check up to 160 frames
            success, frame = cap.read()
            if not success:
                print('Error: Unable to capture video.')
                break
            if cv2.mean(frame)[:3] > (18, 18, 18):  # Use a threshold to check if the frame is not black
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

    def initCodecAvailable(self):
        try:
            result = subprocess.run(['ffmpeg', '-codecs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Encoders:' in line:
                        break
                    if line.startswith(' '):
                        parts = line.split()
                        if len(parts) > 1:
                            self.available_codecs.append(parts[1])
        except FileNotFoundError:
            print("FFmpeg not found. Make sure it is installed and in your system PATH.")

    def serialize(self):
        item_dict = {
            'type': self.item_type,
            'name': self.name,
            'path': self.path,
            'transition': self.cmbTransition.currentText(),
            'option': self.option,
        }

        if self.item_type in ['image', 'pdf_image']:
            duration = int(self.lneStartAt.text()) * 60 + int(self.lneEndAt.text())
            item_dict['duration'] = duration

        return item_dict


if __name__ == '__main__':
    app = QApplication([])
    widget = ItemVideo('video', 'Video 1', 'path/to/video.mp4')
    widget.show()
    app.exec()
