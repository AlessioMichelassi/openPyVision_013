import subprocess

from PyQt6.QtCore import *


class FFmpegCapabilitiesThread(QThread):
    finished = pyqtSignal(str, dict)

    def __init__(self, device_name):
        super().__init__()
        self.device_name = device_name

    def run(self):
        command = f'ffmpeg -f dshow -list_options true -i video="{self.device_name}"'
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            capabilities = self.parse_output(result.stderr)
            self.finished.emit(self.device_name, capabilities)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            self.finished.emit(self.device_name, {})

    def parse_output(self, output):
        capabilities = {}
        current_option = None
        for line in output.split('\n'):
            if 'DirectShow video device options' in line:
                current_option = 'video_options'
                capabilities[current_option] = []
            elif 'pixel_format' in line or 'vcodec' in line:
                if current_option:
                    capabilities[current_option].append(line.strip())
        return capabilities



