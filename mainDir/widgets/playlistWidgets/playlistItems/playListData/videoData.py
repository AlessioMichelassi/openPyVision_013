import json
import cv2
import subprocess
import os
import tempfile

import numpy as np
from PyQt6.QtGui import QImage, QPixmap

from mainDir.widgets.playlistWidgets.playlistItems.playListData.audioData import AudioDataThread


class VideoData:
    """
    Classe per gestire i dati di un video, inclusi informazioni video, audio e miniatura.
    """

    codec = {'avi': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'wmv1', 'wmv2', 'yuv4'],
             'mov': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'mp4': ['libx264', 'libx265', 'mpeg4'],
             'mkv': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
             'webm': ['libvpx', 'libvpx-vp9']}

    def __init__(self, filePath):
        """
        Inizializza la classe VideoData.

        :param filePath: Percorso del file video
        """
        self.filePath = filePath
        self.name = os.path.basename(filePath)
        self.temp_folder = os.path.join(tempfile.gettempdir(), self.name)
        self.video_info = {}
        self.audio_info = {}
        self.thumbnail = None

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
        print(f"Temporary folder created: {self.temp_folder}")  # Stampa il percorso della cartella temporanea
        self.loadData()

    def loadData(self):
        """
        Carica i dati del video. Se le informazioni sono già salvate, le carica dal file JSON.
        Altrimenti, estrae le informazioni dal video e le salva.
        """
        saved_info_path = os.path.join(self.temp_folder, "video_info.json")
        if os.path.exists(saved_info_path):
            try:
                self.loadSavedVideoInfo(saved_info_path)
            except (json.JSONDecodeError, KeyError):
                print(f"Error loading JSON from {saved_info_path}. Recalculating data...")
                self.extractVideoInfo()
                self.extractAudioInfo()
                self.thumbnail = self.getVideoThumbnail(self.filePath)
                self.saveVideoInfo()
        else:
            self.extractVideoInfo()
            self.extractAudioInfo()
            self.thumbnail = self.getVideoThumbnail(self.filePath)
            self.saveVideoInfo()

    def saveVideoInfo(self):
        """
        Salva le informazioni del video e dell'audio in un file JSON e la miniatura in un file PNG.
        """

        def convert_ndarray_to_list(d):
            for key, value in d.items():
                if isinstance(value, np.ndarray):
                    d[key] = value.tolist()
                elif isinstance(value, dict):
                    convert_ndarray_to_list(value)

        video_info = {
            'video_info': self.video_info,
            'audio_info': self.audio_info
        }
        convert_ndarray_to_list(video_info)

        with open(os.path.join(self.temp_folder, "video_info.json"), 'w') as f:
            json.dump(video_info, f)
        if self.thumbnail:
            self.thumbnail.save(os.path.join(self.temp_folder, "thumbnail.png"))

    def loadSavedVideoInfo(self, saved_info_path):
        """
        Carica le informazioni del video e dell'audio dal file JSON salvato.

        :param saved_info_path: Percorso del file JSON salvato
        """
        with open(saved_info_path, 'r') as f:
            video_info = json.load(f)
        self.video_info = video_info['video_info']
        self.audio_info = video_info['audio_info']
        self.thumbnail = QPixmap(os.path.join(self.temp_folder, "thumbnail.png"))

    def extractVideoInfo(self):
        """
        Estrae le informazioni del video utilizzando ffprobe.
        """
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
        """
        Estrae le informazioni audio utilizzando AudioData.
        """
        audio_data = AudioDataThread(self.filePath, self.temp_folder)
        self.audio_info = audio_data.audio_info

    @staticmethod
    def parse_ffprobe_output(output):
        """
        Analizza l'output di ffprobe e lo trasforma in un dizionario.

        :param output: Output di ffprobe
        :return: Dizionario con le informazioni del video
        """
        info_dict = {}
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=')
                info_dict[key.strip()] = value.strip()
        return info_dict

    @staticmethod
    def getVideoThumbnail(path):
        """
        Estrae la miniatura del video.

        :param path: Percorso del file video
        :return: Miniatura del video come QPixmap
        """
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
