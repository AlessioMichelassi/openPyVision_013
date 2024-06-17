import cv2
import numpy as np

# Crea un'immagine di esempio per rappresentare una semplice interfaccia utente
image = np.full((400, 600, 3), 255, dtype=np.uint8)

# Aggiungi alcuni elementi all'interfaccia
cv2.rectangle(image, (50, 50), (250, 150), (0, 255, 0), -1)  # Un pulsante verde
cv2.putText(image, "Button 1", (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

cv2.rectangle(image, (350, 50), (550, 150), (0, 0, 255), -1)  # Un pulsante rosso
cv2.putText(image, "Button 2", (380, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

cv2.rectangle(image, (50, 250), (550, 350), (255, 0, 0), -1)  # Una barra blu
cv2.putText(image, "Status Bar", (230, 310), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

# Crea un oggetto di salienza basato sul residuo spettrale
saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

# Calcola la mappa di salienza
success, saliencyMap = saliency.computeSaliency(image)

# Converti la mappa di salienza in un formato visibile
saliencyMap = (saliencyMap * 255).astype("uint8")

# Trova la regione più saliente
minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(saliencyMap)

# Disegna un cerchio intorno alla regione più saliente
highlighted_image = image.copy()
cv2.circle(highlighted_image, maxLoc, 50, (255, 255, 0), 3)

# Mostra i risultati
cv2.imshow('Original UI', image)
cv2.imshow('Saliency Map', saliencyMap)
cv2.imshow('Highlighted UI', highlighted_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
