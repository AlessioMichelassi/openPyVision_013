import numpy as np
from PyQt6.QtCore import QSize
from mainDir.inputs.baseClass import BaseClass


class SMPTEBarsGenerator(BaseClass):
    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self._frame = self.createBars()

    def createBars(self):
        width, height = self.resolution.width(), self.resolution.height()
        bars = np.zeros((height, width, 3), dtype=np.uint8)

        # Define section heights
        top_section_height = 2 * height // 3
        middle_section_height = height // 12
        bottom_section_height = height // 6

        # Top section colors
        colors_top = [
            (191, 191, 191),  # Grey
            (0, 191, 191),    # Yellow
            (191, 191, 0),    # Cyan
            (0, 191, 0),      # Green
            (191, 0, 191),    # Magenta
            (0, 0, 191),      # Red
            (191, 0, 0)       # Blue
        ]
        bar_width_top = width // len(colors_top)
        for i, color in enumerate(colors_top):
            bars[0:top_section_height, i * bar_width_top:(i + 1) * bar_width_top, :] = color

        # Middle section colors
        colors_middle = [
            (191, 0, 0),    # Blue
            (0, 0, 0),      # Black
            (191, 0, 191),  # Magenta
            (0, 0, 0),      # Black
            (191, 191, 0),  # Cyan
            (0, 0, 0),      # Black
            (191, 191, 191) # Grey
        ]
        bar_width_middle = width // len(colors_middle)
        for i, color in enumerate(colors_middle):
            bars[top_section_height:top_section_height + middle_section_height,
                 i * bar_width_middle:(i + 1) * bar_width_middle, :] = color

        # Bottom section colors
        colors_bottom = [
            (75, 27, 0),     # -I (Blue)
            (255, 255, 255), # White (100 IRE)
            (106, 0, 46),    # +Q (Purple)
            (0, 0, 0),       # Black (0 IRE)
            (0, 0, 0),       # PLUGE
            (0, 0, 0)        # Black (0 IRE)
        ]
        bar_width_bottom = width // 6
        for i, color in enumerate(colors_bottom):
            bars[top_section_height + middle_section_height:, i * bar_width_bottom:(i + 1) * bar_width_bottom, :] = color

        # PLUGE bars
        pluge_bar_width = bar_width_bottom // 3
        pluge_bar_positions = [(0, 3.5), (1, 7.5), (2, 11.5)]
        for i, ire in pluge_bar_positions:
            value = int(255 * (ire / 100))
            bars[top_section_height + middle_section_height:,
                 4 * bar_width_bottom + i * pluge_bar_width:4 * bar_width_bottom + (i + 1) * pluge_bar_width, :] = value

        self._frame = bars
        return bars

    def stop(self):
        super().stop()

    def captureFrame(self):
        self.updateFps()

    def getFrame(self):
        return self._frame


