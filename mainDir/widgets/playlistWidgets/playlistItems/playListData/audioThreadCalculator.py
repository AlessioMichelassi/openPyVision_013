import subprocess
from PyQt6.QtCore import *
import tempfile
import os
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
