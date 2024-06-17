import cv2
import matplotlib.pyplot as plt

# Carica l'immagine in scala di grigi
image = cv2.imread(r'C:\pythonCode\openCVision012\openCVision012\testImage\testImg.png')
r, g, b = cv2.split(image)
# Applica l'equalizzazione dell'istogramma
equalized_r = cv2.equalizeHist(r)
equalized_g = cv2.equalizeHist(g)
equalized_b = cv2.equalizeHist(b)
equalized_image = cv2.merge((equalized_r, equalized_g, equalized_b))

clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

# Applica il CLAHE all'immagine
clahe_r = clahe.apply(r)
clahe_g = clahe.apply(g)
clahe_b = clahe.apply(b)

clahe_image = cv2.merge((clahe_r, clahe_g, clahe_b))

while True:
    cv2.imshow('Immagine Originale', image)
    cv2.imshow('Immagine Equalizzata', equalized_image)
    cv2.imshow('Immagine CLAHE', clahe_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


