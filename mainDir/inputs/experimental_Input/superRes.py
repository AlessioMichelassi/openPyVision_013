import cv2

# Carica il modello di super risoluzione pre-addestrato
sr = cv2.dnn_superres.DnnSuperResImpl_create()

# Scarica il modello pre-addestrato da https://github.com/opencv/opencv_contrib
# e carica il modello scelto (es. 'EDSR_x4.pb' per upscaling 4x)
sr.readModel(r'C:\pythonCode\openCVision012\testImagesFolder\dnnModels\EDSR_x4.pb')

# Imposta il tipo di super risoluzione e il fattore di upscaling
sr.setModel('edsr', 4)

# Carica un'immagine a bassa risoluzione
image = cv2.imread(r"C:\pythonCode\openCVision012\testImagesFolder\len_full.jpg")

# Esegui la super risoluzione
result = sr.upsample(image)
cv2.imwrite(r'C:\pythonCode\openCVision012\testImagesFolder\len_full_superres.jpg', result)
# Mostra l'immagine originale e quella migliorata
cv2.imshow('Low Resolution', image)
cv2.imshow('Super Resolution', result)
cv2.waitKey(0)
cv2.destroyAllWindows()
