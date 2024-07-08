from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtGui import QPixmap
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.baseItem import BaseItem
from mainDir.widgets.playlistWidgets.playlistItems.playListData.imageData import ImageData


class ItemImage(BaseItem):
    """
    Classe per gestire l'interfaccia utente PyQt per i dati delle immagini.
    """

    def __init__(self, filePath=None, parent=None):
        """
        Inizializza la classe ItemImage.

        :param filePath: Percorso del file immagine
        :param parent: Oggetto padre
        """
        super().__init__(parent)
        self.initConnections()
        self.image_data = None
        if filePath:
            self.loadImageFile(filePath)

        self.lneStartAt.setEnabled(False)

    def initConnections(self):
        """
        Inizializza le connessioni dei segnali.
        """
        super().initConnections()
        self.btnLoad.clicked.connect(self.loadItem)

    def loadItem(self):
        """
        Apre una finestra di dialogo per selezionare un file immagine e caricarlo.
        """
        file_filter = "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', file_filter)
        if filePath:
            self.loadImageFile(filePath)

    def loadImageFile(self, filePath):
        """
        Carica il file immagine e aggiorna l'interfaccia utente.

        :param filePath: Percorso del file immagine
        """
        self.image_data = ImageData(filePath)
        self.name = self.image_data.name
        self.path = self.image_data.filePath

        self.setThumbnail(QPixmap(filePath))
        self.setFileName(self.name)
        self.setStartAt("00:00")
        self.setEndAt("00:10")  # Durata predefinita per un'immagine
        self.update()
        self.updateImageLabels(self.image_data.image_info)

    def updateImageLabels(self, image_info):
        """
        Aggiorna le etichette dell'interfaccia utente con le informazioni dell'immagine.

        :param image_info: Dizionario con le informazioni dell'immagine
        """
        self.setMediaCodec(image_info['codec'])
        self.setAudioCodec("No audio")
        self.setVolume("No audio")


if __name__ == '__main__':
    app = QApplication([])
    widget = ItemImage()
    widget.loadItem()
    widget.show()
    app.exec()
