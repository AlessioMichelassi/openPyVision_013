import subprocess
import os
import numpy as np
import soundfile as sf
from PyQt6.QtCore import QThread, pyqtSignal
import scipy.signal as signal
import librosa


class AudioDataThread(QThread):
    audioInfoCalculated = pyqtSignal(dict)

    def __init__(self, video_path, temp_folder):
        super().__init__()
        self.video_path = video_path
        self.temp_folder = temp_folder
        self.audio_info = {}
        self.temp_wav_path = os.path.join(self.temp_folder, "audio.wav")

    def run(self):
        self.extractAudioInfo()
        self.calculateAverageVolume()
        self.calculateSNR()
        self.analyzeSpectralContent()
        self.audioInfoCalculated.emit(self.audio_info)

    def extractAudioInfo(self):
        audio_info_cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
            'stream=codec_name,sample_rate,channels,duration', '-of', 'default=noprint_wrappers=1', self.video_path
        ]
        audio_info = subprocess.run(audio_info_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if audio_info.returncode == 0:
            self.audio_info = self.parse_ffprobe_output(audio_info.stdout)
            duration = float(self.audio_info.get('duration', '0'))
            minutes, seconds = divmod(int(duration), 60)
            self.audio_info['duration_minutes'] = minutes
            self.audio_info['duration_seconds'] = seconds

    def calculateAverageVolume(self):
        cmd = [
            'ffmpeg', '-i', self.video_path, '-vn', '-ac', '2', '-ar', '44100',
            '-y', self.temp_wav_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(self.temp_wav_path):
            print(f"Temporary WAV file created: {self.temp_wav_path}")
            self.audio_info['avg_volumes'] = self.calculate_average_volume_from_wav(self.temp_wav_path)

    def calculateSNR(self):
        if os.path.exists(self.temp_wav_path):
            data, samplerate = sf.read(self.temp_wav_path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            S = librosa.stft(data)
            S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)
            noise_db = np.median(S_db)
            signal_db = np.max(S_db)
            snr = signal_db - noise_db

            self.audio_info['snr'] = snr
            print(f"Calculated SNR: {snr:.2f} dB")

    def analyzeSpectralContent(self):
        if os.path.exists(self.temp_wav_path):
            data, samplerate = sf.read(self.temp_wav_path)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)

            if len(data) < 256:
                print("Audio data is too short for spectral analysis.")
                self.audio_info['spectral_content'] = None
                return

            freqs, times, Sxx = signal.spectrogram(data, samplerate)
            self.audio_info['spectral_content'] = Sxx

    @staticmethod
    def parse_ffprobe_output(output):
        info_dict = {}
        for line in output.split('\n'):
            if '=' in line:
                key, value = line.split('=')
                info_dict[key.strip()] = value.strip()
        return info_dict

    @staticmethod
    def calculate_average_volume_from_wav(wav_path, threshold=0.2):
        data, samplerate = sf.read(wav_path)
        channels = data.shape[1] if len(data.shape) > 1 else 1
        avg_volumes = []
        for ch in range(channels):
            samples = data[:, ch] if channels > 1 else data
            samples = np.abs(samples)
            samples = samples[samples > threshold]
            avg_volume = 20 * np.log10(np.mean(samples)) if samples.size > 0 else -np.inf
            avg_volumes.append(avg_volume)
        return avg_volumes

    def is_audio_poor_quality(self, snr_threshold=20):
        return self.audio_info.get('snr', 0) < snr_threshold
