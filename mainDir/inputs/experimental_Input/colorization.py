import cv2
import numpy as np

# Carica l'immagine
image = cv2.imread(r'C:\pythonCode\openCVision012\openCVision012\testImage\testImg.png', cv2.IMREAD_GRAYSCALE)

import cv2
import numpy as np

# Carica il modello pre-addestrato
proto_file = r"C:\pythonCode\openCVision012\openCVision012\testMethod\models\colorization_deploy_v2.prototxt"
weights_file = "colorization_release_v2.caffemodel"
model = cv2.dnn.readNetFromCaffe(proto_file, weights_file)

# Carica i cluster abbinati
pts_in_hull = np.load('pts_in_hull.npy')  # Punti di riferimento per la colorazione
pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1).astype(np.float32)
model.getLayer(model.getLayerId('class8_ab')).blobs = [pts_in_hull]
model.getLayer(model.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]

# Carica l'immagine in bianco e nero
bw_image = cv2.imread('bw_image.jpg')
h, w = bw_image.shape[:2]

# Preprocessamento dell'immagine
normalized = bw_image.astype("float32") / 255.0
lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)
l_channel = lab[:, :, 0]
l_channel -= 50  # Normalizza il canale L

# Ingresso del modello
blob = cv2.dnn.blobFromImage(l_channel, 1.0, (224, 224), (50, 50, 50), swapRB=False, crop=False)
model.setInput(blob)
ab_channel = model.forward()[0, :, :, :].transpose((1, 2, 0))  # Estrai i canali ab
ab_channel = cv2.resize(ab_channel, (w, h))  # Ridimensiona alla dimensione originale

# Ricostruisci l'immagine
lab_image = np.concatenate((l_channel[:, :, np.newaxis], ab_channel), axis=2)
color_image = cv2.cvtColor(lab_image, cv2.COLOR_LAB2BGR)
color_image = np.clip(color_image, 0, 1)

# Converti in uint8
color_image = (color_image * 255).astype(np.uint8)

# Mostra l'immagine originale e quella colorata
cv2.imshow('Black and White Image', bw_image)
cv2.imshow('Colorized Image', color_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

