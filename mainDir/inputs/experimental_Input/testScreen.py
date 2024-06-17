#  screen(A,B)=1−(1−A)×(1−B)

import cv2
import numpy as np

# Carica due immagini
image1 = cv2.imread(r"C:\Users\aless\Pictures\len_top.jpg") / 255.0
image2 = cv2.imread(r"C:\Users\aless\Pictures\len_top.jpg") / 255.0

# Assicurati che le immagini abbiano la stessa dimensione
image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))

# Operazione di screen
screen_result = 1 - (1 - image1) * (1 - image2)

# Riporta l'immagine al range [0, 255]
screen_result = (screen_result * 255).astype(np.uint8)

# Mostra il risultato
cv2.imshow('Screen Result', screen_result)
cv2.waitKey(0)
cv2.destroyAllWindows()
