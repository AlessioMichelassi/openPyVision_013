import cv2
import numpy as np
import subprocess
import os

"""
Tramite ffmpeg crea un video di esempio con un codec specifico e verifica se può essere letto con OpenCV.
Questo è utile per determinare quali codec sono supportati da OpenCV.
Quindi salva un dizionario con i codici disponibili per ciascun contenitore.
"""


class VideoCaptureSupport:
    def __init__(self):
        self.available_codecs = {}
        self.supportedCodecDictionary = self.init_codec_available()

    @staticmethod
    def create_video_with_ffmpeg(codec, container):
        # Comando FFmpeg per creare un video di esempio
        filename = f'test_{codec}.{container}'
        command = [
            'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=640x480:d=1',
            '-vcodec', codec, filename
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f"Failed to create video with codec {codec} in container {container}: {e.stderr.decode()}")
            return None
        return filename

    def init_codec_available(self):
        # Lista di codec e contenitori comuni
        codecs_containers = {
            'avi': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'wmv1', 'wmv2', 'yuv4'],
            'mov': ['asv1', 'asv2', 'avrn', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
            'mp4': ['libx264', 'libx265', 'mpeg4'],
            'mkv': ['asv1', 'asv2', 'ffv1', 'flv1', 'snow', 'tiff', 'wmv1', 'wmv2', 'yuv4'],
            'webm': ['libvpx', 'libvpx-vp9']
        }

        # Verifica se i video creati possono essere letti con OpenCV
        for container, codecs in codecs_containers.items():
            self.available_codecs[container] = []
            for codec in codecs:
                filename = self.create_video_with_ffmpeg(codec, container)
                if filename:
                    cap = cv2.VideoCapture(filename)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            self.available_codecs[container].append(codec)
                        cap.release()
                    os.remove(filename)

        for container, codecs in self.available_codecs.items():
            print(f"Available codecs for {container}: {codecs}")
        return self.available_codecs

    def get_supported_codec(self):
        return self.supportedCodecDictionary


# Esempio di utilizzo
capture_support = VideoCaptureSupport()
print(capture_support.get_supported_codec())
with open('../../playlistWidgets/playlistItems/supported_codecs.json', 'w') as file:
    file.write(str(capture_support.get_supported_codec()))
