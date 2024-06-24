import atexit
import cProfile
import io
import pstats
import sys

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from mainDir.mainUI_013 import VideoMixerUI
from mainDir.ouputs.mainOut_Viewer import CV_MainOutViewer
from mainDir.widgets.videoWidgets.matrixWidget import MatrixWidget


def setPalette(_app):
    _app.setStyle("Fusion")
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    darkPalette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

    _app.setPalette(darkPalette)


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.timer = QTimer()
        self.mixerVideo = VideoMixerUI()
        self.mixerVideo.synchObject.synch_SIGNAL.connect(self.update)
        self.mainOut = CV_MainOutViewer(np.zeros((1080, 1920, 3), dtype=np.uint8))
        self.mixerVideo.show()

    def update(self):
        dirty_frame = self.mixerVideo.getDirtyFrame()
        if dirty_frame is not None:
            self.mainOut.feedFrame(dirty_frame)


def main():
    app = VideoApp(sys.argv)
    setPalette(app)

    sys.exit(app.exec())


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()


    def exit_handler():
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())


    atexit.register(exit_handler)
    main()
