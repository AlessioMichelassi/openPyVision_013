import cv2
import numpy as np


def create_dark_mask(image, threshold):
    """
    Crea una maschera per le parti scure dell'immagine.

    :param image: Immagine di input in scala di grigi.
    :param threshold: Soglia di intensità per considerare un pixel come scuro.
    :return: Maschera binaria delle parti scure.
    """
    # Crea una maschera binaria dove i pixel più scuri della soglia sono 1
    _, mask = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)
    mask = cv2.blur(mask, (5, 5))
    return mask


def compress_dark_areas(image, mask, compression_factor):
    """
    Applica una compressione alle parti scure dell'immagine.

    :param image: Immagine di input.
    :param mask: Maschera binaria delle parti scure.
    :param compression_factor: Fattore di compressione per le parti scure.
    :return: Immagine con le parti scure compresse.
    """
    # Crea una copia dell'immagine per evitare modifiche in-place
    compressed_image = image.copy()

    # Applica la compressione solo ai pixel selezionati dalla maschera
    compressed_image[mask == 255] = (compressed_image[mask == 255] / compression_factor).astype(np.uint8)

    return compressed_image


# Carica l'immagine
image = cv2.imread(r'C:\pythonCode\openCVision012\openCVision012\testImage\testImg.png')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Crea una maschera per le parti scure
threshold = 100  # Soglia per identificare le parti scure
dark_mask = create_dark_mask(gray_image, threshold)

# Applica la compressione alle parti scure
compression_factor = 2  # Fattore di compressione
compressed_image = compress_dark_areas(image, dark_mask, compression_factor)

# Visualizza l'immagine originale, la maschera e l'immagine compressa
cv2.imshow('Immagine Originale', image)
cv2.imshow('Maschera Parti Scure', dark_mask)
cv2.imshow('Immagine con Parti Scure Compresse', compressed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
