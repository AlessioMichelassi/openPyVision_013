import cv2

# Carica l'immagine
image = cv2.imread(r'C:\pythonCode\openCVision012\testImagesFolder\len_full.jpg')

# Crea un oggetto di salienza basato sul residuo spettrale
saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

# Calcola la mappa di salienza
success, saliencyMap = saliency.computeSaliency(image)

# Converti la mappa di salienza in un formato visibile
saliencyMap = (saliencyMap * 255).astype("uint8")

# Binarizza la mappa di salienza per ottenere una mappa binaria
_, binaryMap = cv2.threshold(saliencyMap, 128, 255, cv2.THRESH_BINARY)

# Mostra i risultati
cv2.imshow('Original Image', image)
cv2.imshow('Saliency Map', saliencyMap)
cv2.imshow('Binary Map', binaryMap)
cv2.waitKey(0)
cv2.destroyAllWindows()
