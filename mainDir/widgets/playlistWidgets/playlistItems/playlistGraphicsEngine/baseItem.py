import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class BaseItem(QWidget):
    """
    Base class for media items in the playlist. Provides common UI elements and functionality
    for displaying and editing media item properties.
    """

    fileTypes = ""
    itemLoaded = pyqtSignal()
    itemEdited = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initialize the BaseItem.

        :param parent: The parent widget.
        """
        super(BaseItem, self).__init__(parent)
        self.fileTypes = ""

        # Main layout components
        self.lblThumbnail = QLabel()
        self.lblMediaCodec = QLabel("h264: 1920x1080@60fps")
        self.lblAudioCodec = QLabel("pcm_s16le: 48000Hz 2ch duration")
        self.lblVolume = QLabel("Avg Vol: Ch1: -11.77dB, Ch2: -11.73dB")
        self.lblFileName = QLabel("avt4.mov")
        self.cmbTransition = QComboBox()
        self.btnLoad = QPushButton("Load")
        self.btnEdit = QPushButton("Edit")
        self.btnRefresh = QPushButton("Refresh")
        self.lblStartAt = QLabel("Start at")
        self.lneStartAt = QLineEdit("00:00")
        self.lblEndAt = QLabel("End at")
        self.lneEndAt = QLineEdit("06:16")
        self.lblBlackFrameOnStart = QLabel("- NoBlackFrameOnStart")
        self.lblBlackFrameOnEnd = QLabel("- black frame start at 00:00 from end")
        self.initUI()
        self.initGeometry()

    def initUI(self):
        """
        Initialize the UI layout and components.
        """
        mainLayout = QHBoxLayout(self)
        mainLayout.addLayout(self.initInfoMedia())
        mainLayout.addWidget(self.createVerticalLine())
        mainLayout.addLayout(self.initControls())
        mainLayout.addWidget(self.createVerticalLine())
        mainLayout.addLayout(self.initTimeline())
        mainLayout.addWidget(self.createVerticalLine())
        mainLayout.addLayout(self.initEditor())
        self.setLayout(mainLayout)

    def initInfoMedia(self):
        """
        Initialize the media information section.

        :return: The layout containing media information widgets.
        """
        infoMediaLayout = QHBoxLayout()
        # Thumbnail
        self.lblThumbnail.setFixedSize(100, 70)
        self.lblThumbnail.setStyleSheet("border: 1px solid black;")
        self.lblThumbnail.setPixmap(QPixmap("thumbnail.png").scaled(128, 72, Qt.AspectRatioMode.KeepAspectRatio))
        infoMediaLayout.addWidget(self.lblThumbnail)
        # Video information
        infoLayout = QVBoxLayout()
        infoLayout.addWidget(self.lblMediaCodec)
        infoLayout.addWidget(self.lblAudioCodec)
        infoLayout.addWidget(self.lblVolume)
        infoMediaLayout.addLayout(infoLayout)
        return infoMediaLayout

    def initControls(self):
        """
        Initialize the control section.

        :return: The layout containing control widgets.
        """
        controlsLayout = QVBoxLayout()
        self.cmbTransition.addItems(["cutToNext", "fadeToNext", "stop", "cutToBlack", "fadeToBlack", "loopForever", "loopNTimes"])
        controlsLayout.addWidget(self.lblFileName)
        controlsLayout.addWidget(self.cmbTransition)
        return controlsLayout

    def initEditor(self):
        """
        Initialize the editor section.

        :return: The layout containing editor buttons.
        """
        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.btnLoad)
        btnLayout.addWidget(self.btnEdit)
        btnLayout.addWidget(self.btnRefresh)
        return btnLayout

    def initTimeline(self):
        """
        Initialize the timeline section.

        :return: The layout containing timeline widgets.
        """
        self.lneStartAt.setFixedWidth(50)
        self.lneEndAt.setFixedWidth(50)

        startLayout = QVBoxLayout()
        startLayout.addWidget(self.lblStartAt)
        startLayout.addWidget(self.lneStartAt)
        startLayout.addWidget(self.lblBlackFrameOnStart)

        endLayout = QVBoxLayout()
        endLayout.addWidget(self.lblEndAt)
        endLayout.addWidget(self.lneEndAt)
        endLayout.addWidget(self.lblBlackFrameOnEnd)

        timelineLayout = QHBoxLayout()
        timelineLayout.addLayout(startLayout)
        timelineLayout.addLayout(endLayout)
        return timelineLayout

    def initConnections(self):
        """
        Initialize signal-slot connections.
        """
        pass

    def initGeometry(self):
        """
        Set the geometry of the widget.
        """
        self.setGeometry(0, 0, 800, 100)

    def createVerticalLine(self):
        """
        Create a vertical line separator.

        :return: The QFrame representing the vertical line.
        """
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def setThumbnail(self, thumbnail):
        """
        Set the thumbnail image.

        :param thumbnail: The QPixmap representing the thumbnail image.
        """
        self.lblThumbnail.setPixmap(thumbnail.scaled(100, 60, Qt.AspectRatioMode.KeepAspectRatio))

    def getThumbnail(self):
        """
        Get the current thumbnail image.

        :return: The QPixmap of the current thumbnail.
        """
        return self.lblThumbnail.pixmap()

    def setMediaCodec(self, media_codec: str):
        """
        Set the media codec information.

        :param media_codec: The media codec information as a string.
        """
        self.lblMediaCodec.setText(media_codec)

    def setAudioCodec(self, audio_codec):
        """
        Set the audio codec information.

        :param audio_codec: The audio codec information as a string.
        """
        self.lblAudioCodec.setText(audio_codec)

    def setVolume(self, volume):
        """
        Set the volume information.

        :param volume: The volume information as a string.
        """
        self.lblVolume.setText(volume)

    def setFileName(self, file_name):
        """
        Set the file name.

        :param file_name: The file name as a string.
        """
        self.lblFileName.setText(file_name)

    def setTransition(self, transition):
        """
        Set the transition type.

        :param transition: The transition type as a string.
        """
        self.cmbTransition.setCurrentText(transition)

    def setStartAt(self, start_at):
        """
        Set the start time.

        :param start_at: The start time as a string.
        """
        self.lneStartAt.setText(start_at)

    def setEndAt(self, end_at):
        """
        Set the end time.

        :param end_at: The end time as a string.
        """
        self.lneEndAt.setText(end_at)

    def setBlackFrameOnStart(self, black_frame_on_start):
        """
        Set the black frame start information.
        Basically when you put a media in preview, you can see a black frame before the media starts.
        The base class while search for an image to use as thumbnail, give you a feedback on how many black frames are
        at the start of the media. So if you have a media with 3 black frames at the start, you can start the media at
        00:01 to avoid the black frames.
        :param black_frame_on_start: The black frame start information as a string.
        """
        self.lblBlackFrameOnStart.setText(black_frame_on_start)

    def setBlackFrameOnEnd(self, black_frame_on_end):
        """
        Set the black frame end information.
        Sometimes when you play a video it's not clear when the video ends. The base class search for the last black
        frame to give you a feedback on how many black frames are at the end of the media. So you can fix the countdown
        during the media playback.
        :param black_frame_on_end: The black frame end information as a string.
        """
        self.lblBlackFrameOnEnd.setText(black_frame_on_end)

    def setFileType(self, file_type):
        """
        Set the file type.

        :param file_type: The file type as a string.
        """
        self.fileTypes = file_type

    def loadItem(self):
        """
        Open a file dialog to select a file and set the file name.
        """
        options = QFileDialog.Options()
        file_filter = f"Files ({self.fileTypes.replace(',', ' ')})"
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select File', '', file_filter, options=options)
        if filePath:
            self.setFileName(filePath.split('/')[-1])
            self.itemLoaded.emit()

    def editItem(self):
        """
        Emit the itemEdited signal.
        """
        print("Edit item")
        self.itemEdited.emit()

    def serialize(self):
        """
        Serialize the item properties to a dictionary.

        :return: A dictionary containing the item properties.
        """
        item_dict = {
            'name': self.lblFileName.text(),
            'path': self.fileTypes,
            'transition': self.cmbTransition.currentText(),
            'start_at': self.lneStartAt.text(),
            'end_at': self.lneEndAt.text(),
            'black_frame_start': self.lblBlackFrameOnStart.text(),
            'black_frame_end': self.lblBlackFrameOnEnd.text(),
            'media_codec': self.lblMediaCodec.text(),
            'audio_codec': self.lblAudioCodec.text(),
            'volume': self.lblVolume.text()
        }
        return item_dict


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = BaseItem()
    widget.show()
    sys.exit(app.exec())
