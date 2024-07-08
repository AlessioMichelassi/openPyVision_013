import os
from PyQt6.QtGui import QImage

class ImageData:
    """
    Classe per gestire i dati di un'immagine.
    """

    def __init__(self, filePath):
        """
        Inizializza la classe ImageData.

        :param filePath: Percorso del file immagine
        """
        self.filePath = filePath
        self.name = os.path.basename(filePath)
        self.image_info = self.getImageInfo(filePath)

    def getImageInfo(self, path):
        """
        Ottiene le informazioni dell'immagine.

        :param path: Percorso del file immagine
        :return: Dizionario con le informazioni dell'immagine
        """
        image = QImage(path)
        width = image.width()
        height = image.height()
        return {
            'width': width,
            'height': height,
            'codec': f"Image: {width}x{height}"
        }
