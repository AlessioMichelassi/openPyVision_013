import json
import subprocess
import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.inputs.deviceProperties.deviceCapabilities import FFmpegCapabilitiesThread
from mainDir.inputs.deviceProperties.deviceUpdaterThread import DeviceUpdater


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Device Capabilities")
        self.resize(600, 400)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.updater = DeviceUpdater()
        self.updater.finished.connect(self.update_devices)
        self.updater.start()

        self.capabilities_threads = []
        self.devices_queue = []

    def update_devices(self, devices):
        self.devices_queue = [devices[key]['name'] for key in devices.keys() if devices[key]['video']]
        self.progress_bar.setMaximum(len(self.devices_queue))
        self.process_next_device()

    def process_next_device(self):
        if not self.devices_queue:
            self.progress_bar.setValue(self.progress_bar.maximum())
            return
        device_name = self.devices_queue.pop(0)
        self.text_edit.append(f"Found video device: {device_name}")
        capabilities_thread = FFmpegCapabilitiesThread(device_name)
        capabilities_thread.finished.connect(self.print_capabilities)
        capabilities_thread.start()
        self.capabilities_threads.append(capabilities_thread)

    def print_capabilities(self, device_name, capabilities):
        c = json.dumps(capabilities, indent=4)
        self.text_edit.append(f"Capabilities for {device_name}:\n{c}\n")
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.process_next_device()

        # Assicurati che il thread corrente venga terminato correttamente
        for thread in self.capabilities_threads:
            thread.quit()
            thread.wait()

        # Uscita dall'applicazione se tutti i dispositivi sono stati elaborati
        if not self.devices_queue and self.progress_bar.value() == self.progress_bar.maximum():
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AppDemo()
    demo.show()
    sys.exit(app.exec())
