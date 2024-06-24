import json
import re

from PyQt6.QtCore import QThread, pyqtSignal, QObject
import subprocess

"""
Open cv non ha un sistema per ottenere informazioni dai dispositivi audio e video.
Quello che si può fare quindi è usare ffmpeg per ottenere queste informazioni. In opencv
bisogna inserire banalmente il numero del dispositivo per poterlo utilizzare, quindi
si può creare un elenco di dispositivi audio e video disponibili e passare il numero
del dispositivo selezionato a opencv.

"""


class DeviceUpdater(QThread):
    finished = pyqtSignal(dict)  # Segnale per inviare i dispositivi trovati

    def __init__(self, isAudio=False):
        super(DeviceUpdater, self).__init__()
        self.isAudio = isAudio

    def run(self):
        command = "ffmpeg -list_devices true -f dshow -i dummy"
        try:
            # Esegui il comando e cattura l'output e gli errori
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            devices = self.parse_devices(result.stderr)
            self.finished.emit(devices)  # Emetti i dispositivi trovati
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            self.finished.emit({})

    def parse_devices(self, output):
        devices = {}
        lines = output.split('\n')
        device_id = 0
        device_info = {}

        for line in lines:
            if "Alternative name" in line:
                alt_name = re.search(r'\"(.+?)\"$', line).group(1)
                device_info['alternative_name'] = alt_name
                devices[device_id] = device_info
                device_id += 1
                device_info = {}
            elif '"' in line:
                name_match = re.search(r'\"(.+?)\"', line)
                if name_match:
                    device_info['name'] = name_match.group(1)
                    if self.isAudio:
                        device_info['audio'] = True
                    else:
                        device_info['video'] = "video" in line

        return devices



