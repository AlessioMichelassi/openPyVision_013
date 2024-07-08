import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys

from mainDir.widgets.playlistWidgets.playlistItems.imageItem012 import ItemImage
from mainDir.widgets.playlistWidgets.playlistItems.videoItem012 import ItemVideo

class ProxyWidget(QWidget):
    def __init__(self, item_type, path, parent=None):
        super().__init__(parent)
        self.item_type = item_type
        self.path = path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.label = QLabel(f"{self.item_type.capitalize()}: {self.path}")
        self.setLayout(layout)
        layout.addWidget(self.label)

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Playlist Manager")

        self.playlist = []
        self.cache = {}  # Cache for storing widgets
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
            self.addItemToList('video', filePath)

    def addImage(self):
        filePath, _ = QFileDialog.getOpenFileName(self, 'Select Image', '', 'Image Files (*.png *.jpg *.jpeg)')
        if filePath:
            self.addItemToList('image', filePath)

    def addItemToList(self, item_type, file_path):
        listItem = QListWidgetItem(self.listWidget)
        widget = ProxyWidget(item_type, file_path)
        listItem.setSizeHint(widget.sizeHint())
        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, widget)
        self.playlist.append({'type': item_type, 'path': file_path})
        self.cache[file_path] = widget

    def updatePlaylist(self):
        self.listWidget.clear()
        for item in self.playlist:
            if item['path'] in self.cache:
                widget = self.cache[item['path']]
            else:
                widget = ProxyWidget(item['type'], item['path'])
                self.cache[item['path']] = widget
            listItem = QListWidgetItem(self.listWidget)
            listItem.setSizeHint(widget.sizeHint())
            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, widget)

    def removeItem(self):
        row = self.listWidget.currentRow()
        if row >= 0:
            item = self.listWidget.takeItem(row)
            if item:
                path = self.playlist[row]['path']
                del self.playlist[row]
                del self.cache[path]

    def moveUpItem(self):
        currentRow = self.listWidget.currentRow()
        if currentRow > 0:
            self.swapItems(currentRow, currentRow - 1)
            self.listWidget.setCurrentRow(currentRow - 1)

    def moveDownItem(self):
        currentRow = self.listWidget.currentRow()
        if currentRow < self.listWidget.count() - 1:
            self.swapItems(currentRow, currentRow + 1)
            self.listWidget.setCurrentRow(currentRow + 1)

    def swapItems(self, fromRow, toRow):
        self.playlist[fromRow], self.playlist[toRow] = self.playlist[toRow], self.playlist[fromRow]
        fromItem = self.listWidget.takeItem(fromRow)
        toItem = self.listWidget.takeItem(toRow)
        self.listWidget.insertItem(fromRow, toItem)
        self.listWidget.insertItem(toRow, fromItem)
        self.listWidget.setItemWidget(toItem, self.cache[self.playlist[fromRow]['path']])
        self.listWidget.setItemWidget(fromItem, self.cache[self.playlist[toRow]['path']])

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
            if isinstance(item_widget, ProxyWidget):
                playlist.append({'type': item_widget.item_type, 'path': item_widget.path})
        return playlist

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Window()
    screen.show()
    sys.exit(app.exec())
