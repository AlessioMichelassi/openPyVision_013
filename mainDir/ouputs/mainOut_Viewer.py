import cv2
import numpy as np
from mainDir.inputs.generator_bars_EBU import FullBarsGenerator
from mainDir.inputs.synchObject import SynchObject


class CV_MainOutViewer:
    color = (190, 190, 255)  # Colore del puntatore laser (Rosso chiaro)

    def __init__(self, image):
        """
        Inizializza il viewer con l'immagine iniziale e imposta i parametri di zoom e pan.
        :param image: L'immagine da visualizzare inizialmente.
        """
        self.image = image
        self.clone = image.copy()
        self.zoom_scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start = None
        self.laser_position = None
        self.is_laser_active = False

        # Nome della finestra deve essere lo stesso per setMouseCallback e namedWindow
        window_name = 'mainOut_Viewer'
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, self.mouse_callback)
        self.update_display()

    def setColor(self, color):
        """
        Imposta il colore del puntatore laser.
        :param color: Il colore del puntatore laser.
        """
        self.color = color

    def setFullScreen(self):
        """
        Imposta la finestra del viewer in modalità schermo intero.
        """
        cv2.setWindowProperty('mainOut_Viewer', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def mouse_callback(self, event, x, y, flags, param):
        """
        Callback per la gestione degli eventi del mouse.
        """
        if event == cv2.EVENT_MBUTTONDOWN:  # Tasto centrale del mouse
            self.drag_start = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.drag_start:
                # Calcola lo spostamento
                dx = x - self.drag_start[0]
                dy = y - self.drag_start[1]
                self.pan_x += dx
                self.pan_y += dy
                self.drag_start = (x, y)
                self.update_display()
            elif self.is_laser_active:
                self.laser_position = (x, y)
                self.update_display()
        elif event == cv2.EVENT_MBUTTONUP:  # Rilascia il tasto centrale del mouse
            self.drag_start = None
        elif event == cv2.EVENT_LBUTTONDOWN:  # Tasto sinistro del mouse
            self.is_laser_active = True
            self.laser_position = (x, y)
            self.update_display()
        elif event == cv2.EVENT_LBUTTONUP:  # Rilascia il tasto sinistro del mouse
            self.is_laser_active = False
            self.laser_position = None
            self.update_display()
        elif event == cv2.EVENT_RBUTTONDOWN:  # Tasto destro del mouse
            # Resetta zoom e pan
            self.pan_x = 0
            self.pan_y = 0
            self.zoom_scale = 1.0
            self.laser_position = None
            self.update_display()
        elif event == cv2.EVENT_MOUSEWHEEL:
            # Zoom avanti/indietro
            if flags > 0:
                self.zoom_scale *= 1.1
            else:
                self.zoom_scale /= 1.1
            self.update_display()

    def update_display(self):
        """
        Aggiorna la visualizzazione dell'immagine tenendo conto di zoom e pan.
        """
        h, w = self.image.shape[:2]
        center_x, center_y = w // 2, h // 2
        # Crea la matrice di trasformazione per lo zoom e il pan
        M = np.float32([
            [self.zoom_scale, 0, center_x - self.zoom_scale * center_x + self.pan_x],
            [0, self.zoom_scale, center_y - self.zoom_scale * center_y + self.pan_y]
        ])
        # Applica la trasformazione all'immagine clonata
        zoomed = cv2.warpAffine(self.clone, M, (w, h))

        if self.laser_position:
            # Disegna il puntatore laser
            pointer = self.draw_laser_pointer(self.laser_position)
            cv2.addWeighted(pointer, 0.8, zoomed, 1 - 0.8, 0, zoomed)

        # Mostra l'immagine
        cv2.imshow('mainOut_Viewer', zoomed)

    def draw_laser_pointer(self, position, diameter=10):
        """
        Disegna un puntatore laser.
        :param position: La posizione del puntatore.
        :param diameter: Il diametro del puntatore.
        :return: L'immagine con il puntatore disegnato.
        """
        x, y = position
        image = np.zeros((1080, 1920, 3), np.uint8)
        cv2.circle(image, (x, y), diameter, self.color, -1)
        return image

    def feedFrame(self, frame):
        """
        Aggiorna l'immagine visualizzata.
        :param frame: Il nuovo frame da visualizzare.
        """
        self.image = frame
        self.clone = frame.copy()
        self.update_display()

    def run(self):
        """
        Esegue il ciclo principale del viewer.
        """
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # Esci con il tasto Esc
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    def updateFrame():
        viewer.feedFrame(input1.getFrame())


    synchObject = SynchObject()
    synchObject.synch_SIGNAL.connect(updateFrame)
    input1 = FullBarsGenerator(synchObject)
    viewer = CV_MainOutViewer(input1.getFrame())
    viewer.run()
