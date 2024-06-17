import numpy as np
import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QHBoxLayout, QSizePolicy


class SpeckleNoiseGenerator(QWidget):
    def __init__(self, resolution=(512, 512), parent=None):
        super().__init__(parent)
        self.resolution = resolution
        self.initUI()
        self.generate_noise()

    def initUI(self):
        self.setWindowTitle('Speckle Noise Generator')
        self.setGeometry(100, 100, self.resolution[1], self.resolution[0])

        self.layout = QVBoxLayout()

        self.image_label = QLabel(self)
        self.layout.addWidget(self.image_label)

        self.button = QPushButton('Generate Speckle Noise', self)
        self.button.clicked.connect(self.generate_noise)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def generate_noise(self):
        # Create a blank image with all pixels set to 1
        image = np.ones(self.resolution, dtype=np.float32)

        # Add speckle noise
        noise = np.random.normal(0, 1, self.resolution)  # Gaussian noise
        speckle_noise = image + image * noise

        # Normalize the image to the range [0, 255]
        speckle_noise = cv2.normalize(speckle_noise, None, 0, 255, cv2.NORM_MINMAX)
        speckle_noise = speckle_noise.astype(np.uint8)

        # Display the image
        self.display_image(speckle_noise)

    def display_image(self, image):
        height, width = image.shape
        bytes_per_line = width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(q_image))
        self.image_label.setFixedSize(width, height)
        self.image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)


if __name__ == "__main__":
    import sys
    from PyQt6.QtGui import QImage, QPixmap

    app = QApplication(sys.argv)
    window = SpeckleNoiseGenerator()
    window.show()
    sys.exit(app.exec())
