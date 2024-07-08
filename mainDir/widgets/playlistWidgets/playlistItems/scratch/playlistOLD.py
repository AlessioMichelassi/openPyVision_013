import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import cv2
import sys

from mainDir.widgets.playlistWidgets.playlistItems.videoItem012 import ItemVideo


class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Playlist Manager")

        self.playlist = []
        self.listWidget = QListWidget()
        self.btnAddVideo = QPushButton("+ Video")
        self.btnAddImage = QPushButton("+ Image")
        self.btnRemoveItem = QPushButton("- Item")
        self.btnMoveUpItem = QPushButton("Move Up")
        self.btnMoveDownItem = QPushButton("Move Down")
        self.btnLoadPlaylist = QPushButton("Load Playlist")
        self.btnSavePlaylist = QPushButton("Save Playlist")
        self.comboPlayMode = QComboBox()
        self.comboPlayMode.addItems(["noLoop", "loop", "randomLoop", "randomPlay"])

        self.initUI()
        self.initConnections()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.btnAddVideo)
        buttonLayout.addWidget(self.btnAddImage)
        buttonLayout.addWidget(self.btnRemoveItem)
        buttonLayout.addWidget(self.btnMoveUpItem)
        buttonLayout.addWidget(self.btnMoveDownItem)
        buttonLayout.addWidget(self.btnLoadPlaylist)
        buttonLayout.addWidget(self.btnSavePlaylist)

        layout.addWidget(self.listWidget)
        layout.addLayout(buttonLayout)
        layout.addWidget(QLabel("Play Mode:"))
        layout.addWidget(self.comboPlayMode)

    def initConnections(self):
        self.listWidget.clicked.connect(self.clicked)
        self.btnAddVideo.clicked.connect(self.addVideo)
        self.btnAddImage.clicked.connect(self.addImage)
        self.btnRemoveItem.clicked.connect(self.removeItem)
        self.btnMoveUpItem.clicked.connect(self.moveUpItem)
        self.btnMoveDownItem.clicked.connect(self.moveDownItem)
        self.btnLoadPlaylist.clicked.connect(self.loadPlaylist)
        self.btnSavePlaylist.clicked.connect(self.savePlaylist)

    def clicked(self, qmodelindex):
        item = self.listWidget.currentItem()
        print(item.text())

    def addVideo(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Video', '', 'Video Files (*.mp4 *.avi)')
        if filePath:
            widget = ItemVideo(filePath)
            self.addItemToList(widget)

    def addImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', 'Image Files (*.png *.jpg *.jpeg)')
        if filePath:
            pass

    def addItemToList(self, widget):
        listItem = QListWidgetItem(self.listWidget)
        listItem.setSizeHint(widget.sizeHint())
        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, widget)

    # def addPDF(self):
    #     filePath, _ = QFileDialog.getOpenFileName(self, 'Select PDF', '', 'PDF Files (*.pdf)')
    #     if filePath:
    #         nicename = filePath.split('/')[-1]
    #         images = self.convertPDFToImages(filePath)
    #         for idx, img in enumerate(images):
    #             image_path = f"{filePath}_page_{idx}.png"
    #             widget = PlaylistItemWidget('pdf_image', f"{nicename} - Page {idx + 1}", image_path, 'cutToNext', 5)
    #             widget.setThumbnail(img)
    #             self.addItemToList(widget)

    # def convertPDFToImages(self, path):
    #     doc = fitz.open(path)
    #     images = []
    #     for page_num in range(len(doc)):
    #         page = doc.load_page(page_num)
    #         pix = page.get_pixmap()
    #         img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGBA8888)
    #         images.append(img)
    #     return images



    def updatePlaylist(self):
        self.listWidget.clear()
        for item in self.playlist:
            widget = PlaylistItemWidget(
                item['type'], item['name'], item['path'], item['transition'], item.get('duration', 0), item.get('option', '')
            )
            if item['type'] == 'video':
                widget.setThumbnail(self.getVideoThumbnail(item['path']))
            elif item['type'] in ['image', 'pdf_image']:
                widget.setThumbnail(QPixmap(item['path']))
            self.addItemToList(widget)

    def removeItem(self):
        row = self.listWidget.currentRow()
        self.listWidget.takeItem(row)

    def moveUpItem(self):
        currentRow = self.listWidget.currentRow()
        if currentRow > 0:
            self.playlist.insert(currentRow - 1, self.playlist.pop(currentRow))
            self.updatePlaylist()
            self.listWidget.setCurrentRow(currentRow - 1)

    def moveDownItem(self):
        currentRow = self.listWidget.currentRow()
        if currentRow < self.listWidget.count() - 1:
            self.playlist.insert(currentRow + 1, self.playlist.pop(currentRow))
            self.updatePlaylist()
            self.listWidget.setCurrentRow(currentRow + 1)

    def loadPlaylist(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Playlist', '', 'Playlist Files (*.json)')
        if filePath:
            with open(filePath, 'r') as file:
                self.playlist = json.load(file)
            self.updatePlaylist()

    def savePlaylist(self):
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save Playlist', '', 'Playlist Files (*.json)')
        if filePath:
            with open(filePath, 'w') as file:
                json.dump(self.getPlaylist(), file, indent=4)

    def getPlaylist(self):
        playlist = []
        for i in range(self.listWidget.count()):
            item_widget = self.listWidget.itemWidget(self.listWidget.item(i))
            playlist.append(item_widget.serialize())
        return playlist


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec())
