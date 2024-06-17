import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap


def enhance_saliency(saliency_map, regions, strengths):
    """
    Aumenta la salienza in specifiche regioni dell'immagine.

    saliency_map: la mappa di salienza originale
    regions: una lista di rettangoli che definiscono le regioni [(x, y, width, height), ...]
    strengths: una lista di fattori di aumento per le regioni corrispondenti
    """
    for (x, y, w, h), strength in zip(regions, strengths):
        saliency_map[y:y + h, x:x + w] += strength
        saliency_map = np.clip(saliency_map, 0, 1)  # Assicura che i valori siano nell'intervallo [0, 1]
    return saliency_map


class SaliencyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

        # Carica l'immagine
        self.image = self.create_demo_image()

        # Crea un oggetto di salienza basato sul residuo spettrale
        self.saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

        # Calcola la mappa di salienza
        success, self.saliency_map = self.saliency.computeSaliency(self.image)
        self.saliency_map = self.saliency_map.astype("float32")

        # Regioni di interesse (pulsanti e barra di stato)
        self.regions = [(50, 50, 200, 100), (350, 50, 200, 100), (50, 250, 500, 100)]

        self.update_image()

    def initUI(self):
        layout = QVBoxLayout()

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        self.slider1 = QSlider(Qt.Horizontal, self)
        self.slider1.setMinimum(-100)

        self.slider1.setMaximum(100)
        self.slider1.setValue(0)
        self.slider1.valueChanged.connect(self.update_image)

        self.slider2 = QSlider(Qt.Horizontal, self)
        self.slider2.setMinimum(-100)
        self.slider2.setMaximum(100)
        self.slider2.setValue(0)
        self.slider2.valueChanged.connect(self.update_image)

        self.slider3 = QSlider(Qt.Horizontal, self)
        self.slider3.setMinimum(-100)
        self.slider3.setMaximum(100)
        self.slider3.setValue(0)
        self.slider3.valueChanged.connect(self.update_image)

        sliders_layout = QHBoxLayout()
        sliders_layout.addWidget(QLabel("Button 1"))
        sliders_layout.addWidget(self.slider1)
        sliders_layout.addWidget(QLabel("Button 2"))
        sliders_layout.addWidget(self.slider2)
        sliders_layout.addWidget(QLabel("Status Bar"))
        sliders_layout.addWidget(self.slider3)

        layout.addLayout(sliders_layout)

        self.setLayout(layout)
        self.setWindowTitle('Saliency Adjustment')
        self.setGeometry(100, 100, 800, 600)

    def create_demo_image(self):
        image = np.full((400, 600, 3), 255, dtype=np.uint8)
        cv2.rectangle(image, (50, 50), (250, 150), (0, 255, 0), -1)
        cv2.putText(image, "Button 1", (80, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.rectangle(image, (350, 50), (550, 150), (0, 0, 255), -1)
        cv2.putText(image, "Button 2", (380, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.rectangle(image, (50, 250), (550, 350), (255, 0, 0), -1)
        cv2.putText(image, "Status Bar", (230, 310), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return image

    def update_image(self):
        strengths = [self.slider1.value() / 100.0, self.slider2.value() / 100.0, self.slider3.value() / 100.0]
        enhanced_saliency_map = enhance_saliency(self.saliency_map.copy(), self.regions, strengths)

        enhanced_saliency_map = (enhanced_saliency_map * 255).astype("uint8")
        highlighted_image = cv2.addWeighted(self.image, 0.7, cv2.applyColorMap(enhanced_saliency_map, cv2.COLORMAP_JET),
                                            0.3, 0)

        height, width, channel = highlighted_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(highlighted_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SaliencyApp()
    ex.show()
    sys.exit(app.exec())
