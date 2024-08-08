import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.imageItem import ItemImage
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.plaListView import PlaylistScene, PlaylistView
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.videoItem013 import ItemVideo


class PlaylistWidget012(QWidget):
    """
    A QWidget class to manage a playlist of images and videos. Provides functionality to add,
    remove, move, save, load, and clear playlist items.
    """
    def __init__(self):
        """
        Initialize the PlaylistWidget.
        """
        super().__init__()
        self.scene = PlaylistScene(self)
        self.view = PlaylistView(self.scene, self)

        self.btnAddImage = QPushButton('Add Image', self)
        self.btnAddVideo = QPushButton('Add Video', self)
        self.btnMoveUp = QPushButton('Move Up', self)
        self.btnMoveDown = QPushButton('Move Down', self)
        self.btnRemove = QPushButton('Remove Item', self)
        self.btnLoadPlaylist = QPushButton('Load Playlist', self)
        self.btnSavePlaylist = QPushButton('Save Playlist', self)
        self.btnClearPlaylist = QPushButton('Clear Playlist', self)
        self.initUI()
        self.initConnections()

    def initUI(self):
        """
        Initialize the user interface layout.
        """
        self.setWindowTitle('Playlist Manager')
        mainLayout = QVBoxLayout(self)
        viewerLayout = QVBoxLayout()
        viewerLayout.addWidget(self.view)
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.btnAddImage)
        btnLayout.addWidget(self.btnAddVideo)
        btnLayout.addWidget(self.btnMoveUp)
        btnLayout.addWidget(self.btnMoveDown)
        btnLayout.addWidget(self.btnRemove)
        btnLayout.addWidget(self.btnLoadPlaylist)
        btnLayout.addWidget(self.btnSavePlaylist)
        btnLayout.addWidget(self.btnClearPlaylist)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addLayout(btnLayout)
        self.setLayout(mainLayout)

    def initConnections(self):
        """
        Initialize the signal-slot connections for the buttons.
        """
        self.btnAddImage.clicked.connect(self.addImage)
        self.btnAddVideo.clicked.connect(self.addVideo)
        self.btnMoveUp.clicked.connect(self.moveItemUp)
        self.btnRemove.clicked.connect(self.removeItem)
        self.btnMoveDown.clicked.connect(self.moveItemDown)
        self.btnSavePlaylist.clicked.connect(self.savePlaylist)
        self.btnLoadPlaylist.clicked.connect(self.loadPlaylist)
        self.btnClearPlaylist.clicked.connect(self.clearPlaylist)

    def addImage(self):
        """
        Add an image item to the playlist.
        """
        item = ItemImage("")
        item.loadItem()
        self.scene.addItemWidget(item)

    def addVideo(self):
        """
        Add a video item to the playlist.
        """
        item = ItemVideo("")
        item.loadItem()
        self.scene.addItemWidget(item)

    def removeItem(self):
        """
        Remove the selected item(s) from the playlist.
        """
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.scene.removeItemWidget(item)

    def moveItemUp(self):
        """
        Move the selected item up in the playlist.
        """
        selected_items = self.scene.selectedItems()
        if selected_items:
            self.scene.moveItemUp(selected_items[0])

    def moveItemDown(self):
        """
        Move the selected item down in the playlist.
        """
        selected_items = self.scene.selectedItems()
        if selected_items:
            self.scene.moveItemDown(selected_items[0])

    def savePlaylist(self):
        """
        Save the current playlist to a JSON file.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Playlist', '', 'JSON Files (*.json);;All Files (*)')
        if file_path:
            self.scene.savePlaylist(file_path)

    def loadPlaylist(self):
        """
        Load a playlist from a JSON file.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, 'Load Playlist', '', 'JSON Files (*.json);;All Files (*)')
        if file_path:
            self.scene.loadPlaylist(file_path)

    def clearPlaylist(self):
        """
        Clear all items from the playlist.
        """
        self.scene.clearPlaylist()


if __name__ == '__main__':
    app = QApplication([])
    widget = PlaylistWidget012()
    widget.show()
    app.exec()
