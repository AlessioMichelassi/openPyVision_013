import cv2
import numpy as np


def enhance_saliency(saliency_map, region, strength):
    """
    Aumenta la salienza in una specifica regione dell'immagine.

    saliency_map: la mappa di salienza originale
    region: il rettangolo che definisce la regione (x, y, width, height)
    strength: il fattore di aumento (può essere negativo per diminuire la salienza)
    """
    x, y, w, h = region
    saliency_map[y:y + h, x:x + w] += strength
    saliency_map = np.clip(saliency_map, 0, 1)  # Assicura che i valori siano nell'intervallo [0, 1]
    return saliency_map


# Carica l'immagine
image = cv2.imread(r'C:\pythonCode\openCVision012\testImagesFolder\len_full.jpg')

# Crea un oggetto di salienza basato sul residuo spettrale
saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

# Calcola la mappa di salienza
success, saliency_map = saliency.computeSaliency(image)

# Converti la mappa di salienza in un formato visibile
saliency_map = (saliency_map * 255).astype("uint8")

# Aumenta la salienza in una regione specifica (ad esempio un rettangolo)
enhanced_saliency_map = saliency_map.astype("float32") / 255.0
enhanced_saliency_map = enhance_saliency(enhanced_saliency_map, (50, 50, 200, 200), 0.5)  # Aumenta la salienza

# Converti la mappa di salienza migliorata in un formato visibile
enhanced_saliency_map = (enhanced_saliency_map * 255).astype("uint8")

# Evidenzia l'immagine originale utilizzando la mappa di salienza migliorata
highlighted_image = cv2.addWeighted(image, 0.7, cv2.applyColorMap(enhanced_saliency_map, cv2.COLORMAP_JET), 0.3, 0)

# Mostra i risultati
cv2.imshow('Original Image', image)
cv2.imshow('Original Saliency Map', saliency_map)
cv2.imshow('Enhanced Saliency Map', enhanced_saliency_map)
cv2.imshow('Highlighted Image', highlighted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
