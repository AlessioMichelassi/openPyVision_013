import json

from mainDir.inputs.deviceProperties.deviceUpdaterThread import DeviceUpdater

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys


    def update_devices(devices):
        d = json.dumps(devices, indent=4)
        print("Devices found:", d)
        updater.quit()
        sys.exit()


    app = QApplication(sys.argv)
    updater = DeviceUpdater()
    updater.finished.connect(update_devices)
    updater.start()
    sys.exit(app.exec())