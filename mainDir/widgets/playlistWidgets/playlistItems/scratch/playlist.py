import json
from PyQt6.QtWidgets import *
import sys

from mainDir.widgets.playlistWidgets.playlistItems.scratch.videoItem012 import ItemVideo


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
            self.playlist.append({'type': 'video', 'path': filePath})

    def addImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', 'Image Files (*.png *.jpg *.jpeg)')
        if filePath:
            # Implement image widget creation here
            # widget = ItemImage(filePath)
            # self.addItemToList(widget)
            # self.playlist.append({'type': 'image', 'path': filePath})
            pass

    def addItemToList(self, widget):
        listItem = QListWidgetItem(self.listWidget)
        listItem.setSizeHint(widget.sizeHint())
        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, widget)

    def updatePlaylist(self):
        self.listWidget.clear()
        for item in self.playlist:
            if item['type'] == 'video':
                widget = ItemVideo(item['path'])
                self.addItemToList(widget)
            elif item['type'] == 'image':
                # Implement image widget creation here
                pass

    def removeItem(self):
        row = self.listWidget.currentRow()
        if row != -1:
            self.listWidget.takeItem(row)
            del self.playlist[row]

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
                json.dump(self.playlist, file, indent=4)


app = QApplication(sys.argv)
screen = Window()
screen.show()
sys.exit(app.exec())
