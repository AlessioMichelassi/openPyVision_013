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

# Define constants for colors
WINDOW_COLOR = QColor(53, 53, 53)
TEXT_COLOR = Qt.GlobalColor.white
BASE_COLOR = QColor(42, 42, 42)
ALTERNATE_BASE_COLOR = QColor(66, 66, 66)
BRIGHT_TEXT_COLOR = Qt.GlobalColor.red
LINK_COLOR = QColor(42, 130, 218)
DISABLED_TEXT_COLOR = QColor(127, 127, 127)
DISABLED_HIGHLIGHT_COLOR = QColor(80, 80, 80)


def setPalette(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()

    # Extract repetitive setting of colors to a function
    def set_color(palette, role, color):
        palette.setColor(role, color)

    # Normal state colors
    set_color(dark_palette, QPalette.ColorRole.Window, WINDOW_COLOR)
    set_color(dark_palette, QPalette.ColorRole.WindowText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Base, BASE_COLOR)
    set_color(dark_palette, QPalette.ColorRole.AlternateBase, ALTERNATE_BASE_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ToolTipBase, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ToolTipText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Text, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Button, WINDOW_COLOR)
    set_color(dark_palette, QPalette.ColorRole.ButtonText, TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.BrightText, BRIGHT_TEXT_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Link, LINK_COLOR)
    set_color(dark_palette, QPalette.ColorRole.Highlight, LINK_COLOR)
    set_color(dark_palette, QPalette.ColorRole.HighlightedText, TEXT_COLOR)

    # Disabled state colors
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, DISABLED_TEXT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, DISABLED_HIGHLIGHT_COLOR)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, DISABLED_TEXT_COLOR)

    app.setPalette(dark_palette)


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
