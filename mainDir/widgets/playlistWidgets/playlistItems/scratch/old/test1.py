import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class BaseItem(QWidget):
    fileTypes = ""

    itemLoaded = pyqtSignal()
    itemEdited = pyqtSignal()

    def __init__(self, parent=None):
        super(BaseItem, self).__init__(parent)
        self.fileTypes = ""

        # Layout principale
        self.lblThumbnail = QLabel()
        self.lblMediaCodec = QLabel("h264: 1920x1080@60fps")
        self.lblAudioCodec = QLabel("pcm_s16le: 48000Hz 2ch duration")
        self.lblVolume = QLabel("Avg Vol: Ch1: -11.77dB, Ch2: -11.73dB")
        self.lblFileName = QLabel("avt4.mov")
        self.cmbTransition = QComboBox()
        self.btnLoad = QPushButton("Load")
        self.btnEdit = QPushButton("Edit")
        self.lblStartAt = QLabel("Start at")
        self.lneStartAt = QLineEdit("00:00")
        self.lblEndAt = QLabel("End at")
        self.lneEndAt = QLineEdit("06:16")
        self.lblBlackFrameOnStart = QLabel("- NoBlackFrameOnStart")
        self.lblBlackFrameOnEnd = QLabel("- black frame start at 00:00 from end")
        self.initUI()

    def initUI(self):
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
        infoMediaLayout = QHBoxLayout()
        # Miniatura
        self.lblThumbnail.setFixedSize(100, 60)
        self.lblThumbnail.setStyleSheet("border: 1px solid black;")
        self.lblThumbnail.setPixmap(QPixmap("thumbnail.png").scaled(128, 72, Qt.AspectRatioMode.KeepAspectRatio))
        infoMediaLayout.addWidget(self.lblThumbnail)
        # Informazioni sul video
        infoLayout = QVBoxLayout()
        infoLayout.addWidget(self.lblMediaCodec)
        infoLayout.addWidget(self.lblAudioCodec)
        infoLayout.addWidget(self.lblVolume)
        infoMediaLayout.addLayout(infoLayout)
        return infoMediaLayout

    def initControls(self):
        # Controlli
        controlsLayout = QVBoxLayout()
        self.cmbTransition.addItems(["cutToNext", "fadeToNext", "stop"])
        controlsLayout.addWidget(self.lblFileName)
        controlsLayout.addWidget(self.cmbTransition)
        return controlsLayout

    def initEditor(self):
        btnLayout = QVBoxLayout()
        btnLayout.addWidget(self.btnLoad)
        btnLayout.addWidget(self.btnEdit)
        return btnLayout

    def initTimeline(self):
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
        pass

    def createVerticalLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def setThumbnail(self, thumbnail):
        self.lblThumbnail.setPixmap(thumbnail.scaled(100, 60, Qt.AspectRatioMode.KeepAspectRatio))

    def setMediaCodec(self, media_codec: str):
        self.lblMediaCodec.setText(media_codec)

    def setAudioCodec(self, audio_codec):
        self.lblAudioCodec.setText(audio_codec)

    def setVolume(self, volume):
        self.lblVolume.setText(volume)

    def setFileName(self, file_name):
        self.lblFileName.setText(file_name)

    def setTransition(self, transition):
        self.cmbTransition.setCurrentText(transition)

    def setStartAt(self, start_at):
        self.lneStartAt.setText(start_at)

    def setEndAt(self, end_at):
        self.lneEndAt.setText(end_at)

    def setBlackFrameOnStart(self, black_frame_on_start):
        self.lblBlackFrameOnStart.setText(black_frame_on_start)

    def setBlackFrameOnEnd(self, black_frame_on_end):
        self.lblBlackFrameOnEnd.setText(black_frame_on_end)

    def setFileType(self, file_type):
        self.fileTypes = file_type

    def loadItem(self):
        options = QFileDialog.Options()
        file_filter = f"Files ({self.fileTypes.replace(',', ' ')})"
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select File', '', file_filter, options=options)
        if filePath:
            self.setFileName(filePath.split('/')[-1])
            self.itemLoaded.emit()

    def editItem(self):
        print("Edit item")
        self.itemEdited.emit()

    def serialize(self):
        item_dict = {
            'type': self.item_type,
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
