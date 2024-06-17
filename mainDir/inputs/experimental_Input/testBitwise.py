import cv2
import numpy as np

# Carica due immagini
image1 = cv2.imread(r"C:\Users\aless\Pictures\len_top.jpg")
image2 = cv2.imread(r"C:\Users\aless\Pictures\indian_head-768x576.jpg")

# Assicurati che le immagini abbiano la stessa dimensione
image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))

# Operazioni bitwise
and_result = cv2.bitwise_and(image1, image2)
or_result = cv2.bitwise_or(image1, image2)
xor_result = cv2.bitwise_xor(image1, image2)
not_result = cv2.bitwise_not(image1)

# Mostra i risultati
cv2.imshow('AND Result', and_result)
cv2.imshow('OR Result', or_result)
cv2.imshow('XOR Result', xor_result)
cv2.imshow('NOT Result', not_result)
cv2.waitKey(0)
cv2.destroyAllWindows()
