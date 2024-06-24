from PyQt6.QtCore import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import *

from mainDir.widgets.videoWidgets.matrixWidgets.stillLoader import StillLoaderWidget


class FilesWidgets(QWidget):
    """
    FilesWidgets class creates a GUI widget with multiple StillLoaderWidgets and associated checkboxes.
    """
    matrix_Signal = pyqtSignal(dict, name="matrix_SIGNAL")

    def __init__(self, parent=None):
        """
        Initialize the FilesWidgets class.

        :param parent: Parent widget, defaults to None.
        """
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        self.still_loader_widgets = []
        self.active_checkboxes = []
        self.labels = ["Stinger1", "Stinger2", "Stinger3", "Still1", "Still2", "Still3",
                       "StillPlaylist", "VideoPlaylist1", "VideoPlaylist2", "VideoPlaylist3"]

        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        """
        Initialize the UI components and layout.
        """
        main_layout = QGridLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(5)

        for i, label_text in enumerate(self.labels):
            # Create label for each input type
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            label.setFixedSize(150, 30)

            # Create StillLoaderWidget for each input
            still_loader = StillLoaderWidget()
            still_loader.setFixedSize(300, 80)

            # Create checkbox to activate/deactivate each input
            btnInputAssign = QCheckBox("Active")
            btnInputAssign.setFixedSize(70, 40)

            # Add widgets to the layout
            main_layout.addWidget(label, i, 0, Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(still_loader, i, 1, Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(btnInputAssign, i, 2, Qt.AlignmentFlag.AlignLeft)

            # Store widgets for later use
            self.still_loader_widgets.append(still_loader)
            self.active_checkboxes.append(btnInputAssign)

        # Create a container widget for the main layout
        container_widget = QWidget()
        container_widget.setLayout(main_layout)

        # Create a scroll area to hold the container widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        # Add the scroll area to the main layout
        self.layout().addWidget(scroll_area)

    def initGeometry(self):
        """
        Set the geometry of the main widget.
        """
        # self.setFixedSize(600, 500)  # Example size, adjust as needed
        pass

    def initConnections(self):
        """
        Initialize the connections between signals and slots.
        """
        for btnInputAssign, still_loader, label_text in zip(self.active_checkboxes,
                                                            self.still_loader_widgets,
                                                            self.labels):
            # Connect the toggled signal of the checkbox to the toggleCapture method
            btnInputAssign.toggled.connect(lambda state, w=still_loader, lt=label_text: self.toggleCapture(state, w, lt))

    def toggleCapture(self, state, still_loader_widget, label_text):
        """
        Handle the toggling of the checkbox to activate/deactivate input capture.

        :param state: The state of the checkbox (True if checked, False if unchecked).
        :param still_loader_widget: The associated StillLoaderWidget.
        :param label_text: The label text for the input.
        """
        # Get widget parameters if the widget has a getDictionary method
        widget_params = still_loader_widget.getDictionary() if hasattr(still_loader_widget, 'getDictionary') else {}

        if state:
            # Emit signal with widget parameters when activated
            self.matrix_Signal.emit({
                "inputName": label_text,
                "deviceType": "StillLoader",
                "deviceName": label_text,
                **widget_params
            })
        else:
            # Emit signal to deactivate input
            self.matrix_Signal.emit({
                "inputName": label_text,
                "deviceType": None,
                "deviceName": None,
                **widget_params
            })


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = FilesWidgets()
    window.show()
    sys.exit(app.exec())
