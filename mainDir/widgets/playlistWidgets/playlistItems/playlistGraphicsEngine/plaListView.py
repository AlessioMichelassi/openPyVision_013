import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.imageItem import ItemImage
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.selectableProxyWidget import \
    SelectableProxyWidget
from mainDir.widgets.playlistWidgets.playlistItems.playlistGraphicsEngine.videoItem013 import ItemVideo


class PlaylistScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items_list = []

    def addItemWidget(self, widget):
        proxy = SelectableProxyWidget(widget)
        self.addItem(proxy)
        self.items_list.append(proxy)
        proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.updateLayout()
        self.updateSelection()

    def removeItemWidget(self, proxy):
        self.removeItem(proxy)
        self.items_list.remove(proxy)
        self.updateLayout()

    def updateLayout(self):
        y = 0
        for item in self.items_list:
            item.setPos(0, y)
            y += item.size().height() + 10

    def updateSelection(self):
        for item in self.items_list:
            item.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.updateSelection()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.updateSelection()

    def moveItemUp(self, proxy):
        index = self.items_list.index(proxy)
        if index > 0:
            self.items_list[index], self.items_list[index - 1] = self.items_list[index - 1], self.items_list[index]
            self.updateLayout()

    def moveItemDown(self, proxy):
        index = self.items_list.index(proxy)
        if index < len(self.items_list) - 1:
            self.items_list[index], self.items_list[index + 1] = self.items_list[index + 1], self.items_list[index]
            self.updateLayout()

    def savePlaylist(self, file_path):
        playlist = []
        for item in self.items_list:
            widget = item.widget()
            if isinstance(widget, ItemImage):
                item_type = 'image'
            elif isinstance(widget, ItemVideo):
                item_type = 'video'
            else:
                continue
            item_data = {
                'type': item_type,
                'path': widget.path
            }
            playlist.append(item_data)
        with open(file_path, 'w') as f:
            json.dump(playlist, f)

    def loadPlaylist(self, file_path):
        with open(file_path, 'r') as f:
            playlist = json.load(f)
        self.clearPlaylist()
        for item_data in playlist:
            item_type = item_data['type']
            item_path = item_data['path']
            if item_type == 'image':
                item = ItemImage(item_path)
            elif item_type == 'video':
                item = ItemVideo(item_path)
            else:
                continue
            self.addItemWidget(item)

    def clearPlaylist(self):
        for item in self.items_list[:]:
            self.removeItemWidget(item)


class PlaylistView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setScene(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setAcceptDrops(True)
        # per fare in modo che gli oggetti siano selezionabili
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRubberBandSelectionMode(Qt.ItemSelectionMode.IntersectsItemShape)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)


# test class

if __name__ == "__main__":
    app = QApplication([])

    scene = PlaylistScene()
    view = PlaylistView(scene)
    view.show()

    app.exec()