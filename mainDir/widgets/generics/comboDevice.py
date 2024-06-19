from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from mainDir.widgets.generics.deviceUpdaterThread import DeviceUpdater

"""
Combo device è una comboBox che usa il thread DeviceUpdater per popolare la lista dei dispositivi.
Quando viene selezionato un dispositivo, viene emesso un segnale con un dizionario contenente l'indice del dispositivo
e il nome del dispositivo.

Open cv non ha un sistema per ottenere informazioni dai dispositivi audio e video.
Quello che si può fare quindi è usare ffmpeg per ottenere queste informazioni. In opencv
bisogna inserire banalmente il numero del dispositivo per poterlo utilizzare, quindi
si può creare un elenco di dispositivi audio e video disponibili e passare il numero
del dispositivo selezionato a opencv.
"""
class ComboDevice(QComboBox):
    deviceChanged = pyqtSignal(dict, name="deviceChanged")
    deviceDictionary = {}
    selectedDictionary = []
    currentIndex = 0

    def __init__(self, parent=None):
        super(ComboDevice, self).__init__(parent)
        self.deviceUpdater = DeviceUpdater(isAudio=False)
        self.deviceUpdater.finished.connect(self.populateCombo)
        self.deviceUpdater.start()
        self.setMinimumWidth(200)
        self.addItem("Select input")  # Add default item
        self.model().item(0).setEnabled(False)  # Disable the first item

    def onDeviceChanged(self, index):
        self.currentIndex = index
        dictio = {"deviceIndex": index - 1,  # Adjust index to match OpenCV
                  "deviceName": self.deviceDictionary.get(index - 1, {}).get('name', 'None')}
        self.deviceChanged.emit(dictio)

    def setSelectedDevice(self, index):
        # Ensure selectedDictionary is large enough
        if index >= len(self.selectedDictionary):
            self.selectedDictionary.extend([None] * (index - len(self.selectedDictionary) + 1))
        self.selectedDictionary[index] = self.deviceDictionary.get(index, {}).get('name', 'None')
        self.clear()
        self.addItem("Select input")  # Add default item
        self.populateCombo(self.deviceDictionary)

    def populateCombo(self, devices):
        self.deviceDictionary = devices
        for key, value in devices.items():
            if value['name'] in self.selectedDictionary:
                continue
            self.addItem(value['name'])
        self.currentIndexChanged.connect(self.onDeviceChanged)

    def getDevicesDictionary(self):
        return self.deviceDictionary

    def getCurrentDeviceSelected(self):
        return {self.currentIndex - 1: self.deviceDictionary.get(self.currentIndex - 1, {}).get('name', 'None')}  # Adjust index


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    combo = ComboDevice()
    combo.deviceChanged.connect(print)
    combo.show()
    sys.exit(app.exec())
