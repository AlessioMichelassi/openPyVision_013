from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.widgets.playlistWidgets.playlistItems.playlist012 import PlaylistWidget012


class PlaylistControlWidget(QWidget):
    playlistLoaded = pyqtSignal(str, name="playlistLoaded")
    playlistSaved = pyqtSignal(str, name="playlistSaved")
    playlistEdited = pyqtSignal(name="playlistEdited")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playlist = PlaylistWidget012()
        layout = QHBoxLayout(self)

        # Pulsante per caricare la playlist
        self.btnLoadPlaylist = QPushButton("Load Playlist", self)
        self.btnLoadPlaylist.clicked.connect(self.loadPlaylist)
        layout.addWidget(self.btnLoadPlaylist)

        # Pulsante per salvare la playlist
        self.btnSavePlaylist = QPushButton("Save Playlist", self)
        self.btnSavePlaylist.clicked.connect(self.savePlaylist)
        layout.addWidget(self.btnSavePlaylist)

        # Pulsante per editare la playlist
        self.btnEditPlaylist = QPushButton("Edit Playlist", self)
        self.btnEditPlaylist.clicked.connect(self.editPlaylist)
        layout.addWidget(self.btnEditPlaylist)

        self.setLayout(layout)

    def loadPlaylist(self):
        """
        Open a file dialog to select a playlist file and emit the playlistLoaded signal.
        """
        file_path, _ = QFileDialog.getOpenFileName(self, 'Load Playlist', '', 'JSON Files (*.json);;All Files (*)')
        if file_path:
            self.playlistLoaded.emit(file_path)

    def savePlaylist(self):
        """
        Open a file dialog to save a playlist file and emit the playlistSaved signal.
        """
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Playlist', '', 'JSON Files (*.json);;All Files (*)')
        if file_path:
            self.playlistSaved.emit(file_path)

    def editPlaylist(self):
        """
        Emit the playlistEdited signal to indicate that the playlist should be edited.
        """
        self.playlist.show()
        self.playlistEdited.emit()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    playlistControlWidget = PlaylistControlWidget()

    # Connessioni di esempio per i segnali
    playlistControlWidget.playlistLoaded.connect(lambda path: print(f"Playlist loaded from: {path}"))
    playlistControlWidget.playlistSaved.connect(lambda path: print(f"Playlist saved to: {path}"))
    playlistControlWidget.playlistEdited.connect(lambda: print("Playlist edited"))

    playlistControlWidget.show()
    sys.exit(app.exec())
