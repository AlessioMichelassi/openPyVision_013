## **4.0 \- Video Mixing**


![melies](https://github.com/AlessioMichelassi/openPyVision_013/blob/master/wiki/imgs/image46.jpg)
The simplest way to mix two images together is to add them. It may sound crazy, but this is mathematically what was done with film, and the result was once called “double exposure.” If the subject is shot against a black background, adding it to another image creates a ghostly effect. Georges Méliès created hundreds of films using this technique.

```python
out_image = clamp(input1 + input2)
```

This approach is a direct translation of the analog method used in film, where multiple exposures were summed to create a final image. Practically, if the subject is shot against a black background and then added to another image, you get a ghostly effect. The simplicity of this operation makes it easy to understand how images can be combined, but it also introduces limitations such as value clamping.

In graphic design software, mathematical operations on pixels are often referred to as "Blending Modes." In Photoshop, the “Add” operation is known as “Color Dodge.” Other blending modes include “Screen” and “Lighten,” which achieve similar effects with different mathematical operations that help mitigate clamping issues. You can delve into the mathematics behind blending modes on pegtop.net, where Jens Gruschel maintains a blog describing the mathematics used by graphics engines ([https://www.pegtop.net/delphi/articles/blendmodes/](https://www.pegtop.net/delphi/articles/blendmodes/)).

## **4.1 \- MixBus**

We introduced the double exposure technique used by Méliès at the turn of the 19th century. His method was to shoot a background with, for example, a black area and then, by rewinding the film, the completely black area remained unexposed and could be exposed again. This trick, known as double exposure, was widely used until the advent of digital special effects.

In digital, the technique is based on managing the transparency of an image, saying that black is completely transparent, white is completely opaque, and medium gray (0.5) is semi-transparent. The mathematical formula to achieve this, as Szelinski from Washington University reminds us ([http://szeliski.org/Book/](http://szeliski.org/Book/)), is:

```python
I_out = alpha1 * I1 + (alpha2) * I2
```

where α1 and α2 are values from 0 to 1 indicating the transparency of the images. In our case, when we mix, we want one of the two images to become increasingly transparent while the other becomes increasingly opaque. So, they will have a common α, and the formula becomes:

```python
I_out = alpha * I1 + (1-alpha) * I2
```

Our α is obviously variable, so by moving the mix lever, we take it from 0 to 1, and pulling it down does the opposite. Mixers also have a button for automatic mixing, so the logic of the operation becomes more complex.

To achieve a mix without worrying about whether the slider or the button is used, we can assume there is always a live image called "program," and the "fade" variable can only move in one direction from 0 to 1. This way, when we mix with the slider or button, we always move the variable from 0 to 1, changing the opacity of the "preview."

What we need to do is create a MixBus, a video channel that always contains two images: one that is always completely transparent (the preview) and one that is always completely opaque (the program). If we move the slider, we increase the opacity of the preview and decrease that of the program. When we reach 1, we make the cut, swap the signals, and reset the fade variable.

To perform the weighted sum of the two images in OpenCV, you can use:

```python
cv2.addWeighted(input1, alpha1, input2, alpha2, gamma)
```

You can then create a file `mixBus.py`:

```python
class mixBus(QObject):  
    _fade = 0  
    fadeTime = 100

    def __init__(self, input1, input2, parent=None):  
        super().__init__(parent)  
        self.previewInput = input1  
        self.programInput = input2  
        self.autoMix_timer = QTimer(self)  
        self.autoMix_timer.timeout.connect(self._fadeTo)

    def getMixed(self):  
        prw_frame = self.previewInput.getFrame()  
        prg_frame = self.programInput.getFrame()  
        if self._fade == 0:  
            return prw_frame, prg_frame  
        else:  
            return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)

    def cut(self):  
        self._fade = 0  
        self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):  
        self.autoMix_timer.start(self.fadeTime)

    def _fadeTo(self):  
        self._fade += 0.1  
        if self._fade > 1:  
            self.autoMix_timer.stop()  
            self.cut()

    def fadeTo(self, value: int):  
        if value == 0:  
            self._fade = 0  
        else:  
            self._fade = value/100
```

With this class, we can perform automatic and manual mixes and cuts once we pass the references of two inputs. To do this, we create a widget with two labels, one for the preview and one for the program. We add a button for cutting, one for AutoMix, and a slider for manual mixing. We use a color generator as input1 and a noise generator as input2.

```python
class testMixBus(QWidget):  
    def __init__(self, synchObject, parent=None):  
        super().__init__(parent)  
        self.syncObject = synchObject  
        self.input1 = ColorGenerator(self.syncObject)  
        self.input2 = RandomNoiseGenerator(self.syncObject)  
        self.mixBus = mixBus(self.input1, self.input2)  
        self.lblPreview = QLabel()  
        self.lblProgram = QLabel()  
        self.btnCut = QPushButton("CUT")  
        self.btnAutoMix = QPushButton("AutoMix")  
        self.sldFade = QSlider()  
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)  
        self.sldFade.setRange(0, 100)  
        self.initUI()  
        self.initGeometry()  
        self.initConnections()

    def initUI(self):  
        mainLayout = QVBoxLayout()  
        viewerLayout = QHBoxLayout()  
        viewerLayout.addWidget(self.lblPreview)  
        viewerLayout.addWidget(self.lblProgram)  
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)  
        buttonLayout = QHBoxLayout()  
        buttonLayout.addItem(spacer)  
        buttonLayout.addWidget(self.btnCut)  
        buttonLayout.addWidget(self.btnAutoMix)  
        buttonLayout.addWidget(self.sldFade)  
        mainLayout.addLayout(viewerLayout)  
        mainLayout.addLayout(buttonLayout)  
        self.setLayout(mainLayout)

    def initGeometry(self):  
        self.lblPreview.setFixedSize(640, 360)  
        self.lblProgram.setFixedSize(640, 360)

    def initConnections(self):  
        self.syncObject.synch_SIGNAL.connect(self.updateFrame)  
        self.btnCut.clicked.connect(self.cut)  
        self.btnAutoMix.clicked.connect(self.autoMix)  
        self.sldFade.valueChanged.connect(self.setFade)

    def updateFrame(self):  
        prw_frame, prg_frame = self.mixBus.getMixed()  
        prw_frame = cv2.resize(prw_frame, (640, 360))  
        prg_frame = cv2.resize(prg_frame, (640, 360))  
        prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)  
        prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)  
        self.lblPreview.setPixmap(QPixmap.fromImage(prw_image))  
        self.lblProgram.setPixmap(QPixmap.fromImage(prg_image))

    def cut(self):  
        self.mixBus.cut()

    def autoMix(self):  
        self.mixBus.autoMix()

    def setFade(self):  
        self.mixBus.setFade(self.sldFade.value())
```

```python
if __name__ == '__main__':  
    import sys  
    app = QApplication(sys.argv)  
    synchObject = SynchObject()  
    test = testMixBus(synchObject)  
    test.show()  
    sys.exit(app.exec())  
```

![mixBus Fade](https://github.com/AlessioMichelassi/openPyVision_013/blob/master/wiki/imgs/image30_MixFade.gif)

With this implementation, you can see in real-time how different image blending methods work, using both manual and automatic mixing.

## **4.2 - Wipe Left to Right**

In the previous chapter, we saw how to use NumPy for slicing a matrix. We can think of a "wipe" transition similarly to slicing. During the transition, the resulting image is composed of a part of the preview image and a part of the program image.

When the **`_fade`** variable is at 0, we see the program image completely. When **`_fade`** is at 0.5, we see half of the screen with the preview image and the other half with the program image. Finally, when **`_fade`** reaches 1, we see only the preview image. Just like with the "mix" transition, we reset the **`_fade`** variable to 0, stop the timer, and perform the "cut."

Experimentally, I noticed that even though the operation is done correctly and in time, the animation sometimes appears choppy. I believe the issue is due to the on-the-fly creation of a **`wipePosition`**. To resolve this, I precomputed a list of positions in the init phase.

The "wipe" transition uses a precomputed list of positions to ensure smooth and consistent movement. At each timer interval, we update the wipe position using NumPy slicing to combine the two images based on the current position.

Here is how the left-to-right wipe is implemented:

* **Initializing the wipe positions**: A list of positions is created using **`np.linspace`**, which divides the width of the image (1920 pixels) into a number of steps determined by the wipe time (**`_wipeTime`**).  
* **Updating the position**: At each timer interval, the wipe position is updated by incrementing a counter (**`_wipe`**). The current position is then used to combine the preview and program images.  
* **Combining the images**: Using NumPy slicing, the two images are combined based on the current wipe position.

This implementation ensures that the wipe movement is smooth and that the resulting image is a dynamic combination of the two images, based on the current wipe position.

Here is an example of the code that shows how to implement the "wipe" transition:

```python
def wipeLeftToRight(self, preview_frame, program_frame):  
   wipe_position = int(self._wipe_position_list[self._wipe])  
   wipe_frame = program_frame.copy()  
   wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]  
   return wipe_frame
```

The complete code becomes:

```python
import time  
from enum import Enum
import cv2  
import numpy as np  
from PyQt6.QtCore import *  
from PyQt6.QtGui import QImage, QPixmap  
from PyQt6.QtWidgets import *
from cap5.cap5_4.colorGenerator import ColorGenerator  
from cap5.cap5_4.randomNoiseGenerator import RandomNoiseGenerator  
from cap5.cap5_4.synchObject import SynchObject

class MIX_TYPE(Enum):  
   FADE = 0  
   WIPE_LEFT_TO_RIGHT = 1  
   WIPE_RIGHT_TO_LEFT = 2  
   WIPE_TOP_TO_BOTTOM = 3  
   WIPE_BOTTOM_TO_TOP = 4

class mixBus5_6(QObject):  
   _fade = 0  
   fadeTime = 100  
   _wipe = 0  
   _wipeTime = 90  
   effectType = MIX_TYPE.WIPE_LEFT_TO_RIGHT

   def __init__(self, input1, input2, parent=None):  
       super().__init__(parent)  
       self.previewInput = input1  
       self.programInput = input2  
       self.autoMix_timer = QTimer(self)  
       self.autoMix_timer.timeout.connect(self._fader)  
       self._init_wipe_positions()

   def _init_wipe_positions(self):  
       _wipe_step = max(1, self._wipeTime)  
       self._wipe_position_list = np.linspace(0, 1920, _wipe_step)

   def getMixed(self):  
       prw_frame = self.previewInput.getFrame()  
       prg_frame = self.programInput.getFrame()  
       if self._fade == 0:  
           return prw_frame, prg_frame  
       else:  
           if self.effectType == MIX_TYPE.FADE:  
               return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)  
           elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:  
               return prw_frame, self.wipeLeftToRight(prw_frame, prg_frame)

   def setFade(self, value: int):  
       if value == 0:  
           self._fade = 0  
       else:  
           self._fade = value / 100

   def cut(self):  
       self._fade = 0  
       self._wipe = 0  
       self.previewInput, self.programInput = self.programInput, self.previewInput

   def autoMix(self):  
       self.autoMix_timer.start(1000 // 60)

   def _fader(self):  
       if self.effectType == MIX_TYPE.FADE:  
           self._fade += 0.01  
           if self._fade > 1:  
               self.autoMix_timer.stop()  
               self.cut()  
       elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:  
           self._wipe += 1  
           self._fade += 0.01  
           if self._wipe > len(self._wipe_position_list)-1:  
               self.autoMix_timer.stop()  
               self.cut()

   def wipeLeftToRight(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]  
       return wipe_frame
```

## **4.3 Wipe Right to Left**

To reverse the wipe so that it goes from right to left, we can create a list of positions using **`np.linspace`** that goes from 1920 to 0. This allows us to have a series of decreasing positions, starting from the right side of the image and moving towards the left side.

During the wipe, we combine the preview and program images using NumPy slicing. Instead of using:

```python
wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
```

we use:

```python
wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]
```

This is because we want the preview image to gradually appear from the right side. With this logic, the pixels to the right of the current position (**`wipe_position`**) are replaced by the pixels from the preview image, creating a reverse wipe effect.

```python
class MIX_TYPE(Enum):  
   FADE = 0  
   WIPE_LEFT_TO_RIGHT = 1  
   WIPE_RIGHT_TO_LEFT = 2  
   WIPE_TOP_TO_BOTTOM = 3  
   WIPE_BOTTOM_TO_TOP = 4

class MixBus4_3(QObject):  
   _fade = 0  
   fadeTime = 100  
   _wipe = 0  
   _wipeTime = 90  
   effectType = MIX_TYPE.WIPE_LEFT_TO_RIGHT

   def __init__(self, input1, input2, parent=None):  
       super().__init__(parent)  
       self.previewInput = input1  
       self.programInput = input2  
       self.autoMix_timer = QTimer(self)  
       self.autoMix_timer.timeout.connect(self._fader)  
       self._init_wipe_positions()

   def _init_wipe_positions(self):  
       _wipe_step = max(1, self._wipeTime)  
       self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)  
       self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)  
       self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)  
       self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)

   def getMixed(self):  
       prw_frame = self.previewInput.getFrame()  
       prg_frame = self.programInput.getFrame()  
       if self._fade == 0:  
           return prw_frame, prg_frame  
       else:  
           if self.effectType == MIX_TYPE.FADE:  
               return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)  
           elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:  
               return prw_frame, self.wipeLeftToRight(prw_frame, prg_frame)  
           elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:  
               return prw_frame, self.wipeRightToLeft(prw_frame, prg_frame)

   def setFade(self, value: int):  
       if value == 0:  
           self._fade = 0  
       else:  
           self._fade = value / 100  
           self._wipe = value

   def cut(self):  
       self._fade = 0  
       self._wipe = 0  
       self.previewInput, self.programInput = self.programInput, self.previewInput

   def autoMix(self):  
       self.autoMix_timer.start(1000 // 60)

   def _fader(self):  
       if self.effectType == MIX_TYPE.FADE:

  
           self._fade += 0.01  
           if self._fade > 1:  
               self.autoMix_timer.stop()  
               self.cut()  
       elif self.effectType in [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT]:  
           self._wipe += 1  
           self._fade += 0.01  
           if self._wipe > len(self._wipe_position_leftToRight_list) - 1:  
               self.autoMix_timer.stop()  
               self.cut()

   def wipeLeftToRight(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_leftToRight_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]  
       return wipe_frame

   def wipeRightToLeft(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_rightToLeft_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]  
       return wipe_frame
```

## **4.4 Wipe Up and Down**

To implement a vertical wipe, either from top to bottom or from bottom to top, we use a logic similar to the horizontal wipe, but with the rows of the image instead of the columns.

For the top-to-bottom wipe, we create a list of positions with **`np.linspace`** that ranges from 0 to 1080 (the height of the image), and similarly, we create another one to go from 1080 to 0. At each timer step, we use NumPy slicing to combine the two images based on the current wipe position.

During the wipe, we use slicing to copy the rows from the preview over the corresponding rows from the program:

```python
def wipeTopToBottom(self, preview_frame, program_frame):  
   wipe_position = int(self._wipe_position_topToBottom_list[self._wipe])  
   wipe_frame = program_frame.copy()  
   wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]  
   return wipe_frame
```

For the bottom-to-top wipe, we use NumPy slicing to replace the rows below the current position (**`wipe_position`**) with the corresponding rows from the preview image. For the top-to-bottom wipe, we use NumPy slicing to replace the rows above the current position (**`wipe_position`**) with the corresponding rows from the preview image.

This approach ensures that the wipe movement is smooth and that the resulting image is a dynamic combination of the two images, based on the current wipe position.

```python
class MIX_TYPE(Enum):  
   FADE = 0  
   WIPE_LEFT_TO_RIGHT = 1  
   WIPE_RIGHT_TO_LEFT = 2  
   WIPE_TOP_TO_BOTTOM = 3  
   WIPE_BOTTOM_TO_TOP = 4

class MixBus4_4(QObject):  
   _fade = 0  
   fadeTime = 100  
   _wipe = 0  
   _wipeTime = 90  
   effectType = MIX_TYPE.FADE

   def __init__(self, input1, input2, parent=None):  
       super().__init__(parent)  
       self.previewInput = input1  
       self.programInput = input2  
       self.autoMix_timer = QTimer(self)  
       self.autoMix_timer.timeout.connect(self._fader)  
       self._init_wipe_positions()

   def _init_wipe_positions(self):  
       _wipe_step = max(1, self._wipeTime)  
       self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)  
       self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)  
       self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)  
       self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)

   def getMixed(self):  
       prw_frame = self.previewInput.getFrame()  
       prg_frame = self.programInput.getFrame()  
       if self._fade == 0:  
           return prw_frame, prg_frame  
       else:  
           if self.effectType == MIX_TYPE.FADE:  
               return prw_frame, cv2.addWeighted(prw_frame, self._fade,   
                                             prg_frame, 1 - self._fade, 0)  
           elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:  
               return prw_frame, self.wipeLeftToRight(prw_frame, prg_frame)  
           elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:  
               return prw_frame, self.wipeRightToLeft(prw_frame, prg_frame)  
           elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:  
               return prw_frame, self.wipeTopToBottom(prw_frame, prg_frame)  
           elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:  
               return prw_frame, self.wipeBottomToTop(prw_frame, prg_frame)

   def setFade(self, value: int):  
       if value == 0:  
           self._fade = 0  
       else:  
           self._fade = value / 100  
           self._wipe = value

   def cut(self):  
       self._fade = 0  
       self._wipe = 0  
       self.previewInput, self.programInput = self.programInput, self.previewInput

   def autoMix(self):  
       self.autoMix_timer.start(1000 // 60)

   def _fader(self):  
       if self.effectType == MIX_TYPE.FADE:  
           self._fade += 0.01  
           if self._fade > 1:  
               self.autoMix_timer.stop()  
               self.cut()  
       elif self.effectType in [MIX_TYPE.WIPE_LEFT_TO_RIGHT,  
                                MIX_TYPE.WIPE_RIGHT_TO_LEFT,  
                                MIX_TYPE.WIPE_TOP_TO_BOTTOM,  
                                MIX_TYPE.WIPE_BOTTOM_TO_TOP]:  
           self._wipe += 1  
           self._fade += 0.01  
           if self._wipe > len(self._wipe_position_leftToRight_list) - 1:  
               self.autoMix_timer.stop()  
               self.cut()

   def wipeLeftToRight(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_leftToRight_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]  
       return wipe_frame

   def wipeRightToLeft(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_rightToLeft_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]  
       return wipe_frame

   def wipeTopToBottom(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_topToBottom_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]  
       return wipe_frame

   def wipeBottomToTop(self, preview_frame, program_frame):  
       wipe_position = int(self._wipe_position_bottomToTop_list[self._wipe])  
       wipe_frame = program_frame.copy()  
       wipe_frame[wipe_position:, :] = preview_frame[wipe_position:, :]  
       return wipe_frame
```

## **4.5 Stinger**

A stinger is a sequence of images used instead of a wipe transition. Typically, it is an animation that introduces a full-screen logo, and while the logo is on screen, a cut is made between the preview and program. This technique is widely used to introduce videos, replays in sports, the start and end of commercial breaks, and so on.

These image sequences have an additional channel called alpha or matte. This fourth channel is a black-and-white map used to determine the transparency of the image. Where the values are zero (black), the image is completely transparent, while where the values are 255 (white), the image is completely opaque. Intermediate values make the image semi-transparent.

To composite two images together, the two matrices must be identical in dimensions and type, so they must be two matrices of \[1920x1080, 3\]. The compositing operation can be described by the following formula:

\[ \text{output} = \text{program} \times (1 - \alpha) + \text{stinger} \times \alpha \]

Let's take a look at an image of the stinger:

![][image20]![][image21]

As mentioned, this image has four channels: the first three, b, g, r, are the color channels, while the fourth is an image, shown next to it, in black and white, which identifies the points where the image is transparent (black or zero) or completely opaque (255 or white).

![][image22]![][image23]

To mix it with another image, the procedure is as follows: if we invert the alpha channel, we obtain its negative, which, when multiplied by our program image, will appear black in the areas where the stinger is not black, and similarly, the stinger will appear black in the areas where its alpha value indicates it should be completely transparent. By adding the two images together, we get the composite image:

![][image24]

This technique is the mathematical equivalent of what was done in film. The black represented the unexposed part of the film, the part that was still untouched. With an optical printer, masks were created on acetate sheets, called Matte, leaving the part that was black for us transparent and painting the part that was white for us black. In this way, a copy of the live-action film was made with these holes in the image. The process was repeated using another image with the negative of the matte, and then the two films were projected simultaneously and copied onto a new film.

You can learn more about the techniques used by starting with the Wikipedia article on [optical printers](https://en.wikipedia.org/wiki/Optical_printer).

To recreate this technique and perform it in real-time, I conducted various experiments to find the best method for performing this operation. Matrix multiplication is an expensive operation; however, I realized that many of the required operations can be precomputed, so the results are already calculated when needed. Let's examine the list of necessary operations:

1. Split the channels of the stinger image:  
   	b, g, r, a = SPLIT(stinger)  
2. Create an alpha matrix replicated across three channels:  
   	α = MERGE(a, a, a)  
3. Calculate the overlay by multiplying the b, g, r channels by alpha:  
   	overlay = MERGE(b, g, r) × α  
4. Invert the alpha:  
   	iA = 1 − a  
   	invert_alpha = MERGE(iA, iA, iA)  
5. Calculate the background:  
   	background = program × invert_alpha  
6. Add background and overlay:  
   	output = background + overlay

Each operation introduces a small delay. To reduce this issue, we can precompute some operations when loading the stinger. We can create a special class that pre-processes the stinger images and provides the precomputed results through functions like **`getInvAlpha(index)`** or **`getPremultiplyStinger(index)`**. This way, the real-time calculation is reduced to just two operations.

```python
import os  
import time  
import cv2  
import numpy as np  
from PyQt6.QtCore import QObject

class StingerInputLoader(QObject):  
   def __init__(self, parent=None):  
       super().__init__(parent)  
       self.stingerPath = ''  
       self.stingerImages = []  # original list of images with alpha channel  
       self.stingerRGBImages = []  # list of images without alpha channel  
       self.stingerAlphaImages = []  # list of alpha channel images  
       self.stingerInvAlphaImages = []  # list of inverted alpha channel images  
       self.stingerPreMultipliedImages = []  # list of pre-multiplied images

   def setPath(self, path):  
       self.stingerPath = path  
       self.loadStingerFrames(path)  
       self._findAlphaInvertAndMerge(self.stingerImages)

   def getStingerFrame(self, index):  
       return self.stingerImages[index]

   def getStingerAlphaFrame(self, index):  
       return self.stingerAlphaImages[index]

   def getStingerInvAlphaFrame(self, index):  
       return self.stingerInvAlphaImages[index]

   def getStingerPremultipliedFrame(self, index):  
       return self.stingerPreMultipliedImages[index]

   def _findAlphaInvertAndMerge(self, imageList):  
       for image in imageList:  
           b, g, r, a = cv2.split(image)  
           alpha = cv2.merge((a, a, a))  
           invA = cv2.bitwise_not(a)  
           invAlpha = cv2.merge((invA, invA, invA))  
           bgr = cv2.merge((b, g, r))  
           self.stingerAlphaImages.append(alpha)  
           self.stingerInvAlphaImages.append(invAlpha)  
           self.stingerRGBImages.append(bgr)  
           self.stingerPreMultipliedImages.append(cv2.multiply(alpha, bgr))

   def loadStingerFrames(self, path):  
       for filename in os.listdir(path):  
           if filename.endswith('.png'):  
               image_path = os.path.join(path, filename)  
               image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  
               self.stingerImages.append(image)

if __name__ == '__main__':  
   path = r'\\openPyVisionBook\\openPyVisionBook\\cap5\\cap5_5\\stingerTest'  
   stingerInputLoader = StingerInputLoader()

   timeStart = time.time()  
   stingerInputLoader.setPath(path)  
   print(f"Time to load stinger frames: {time.time() - timeStart} seconds")
```

Time to load stinger frames: 2.4963250160217285 seconds
![stinger](imgs/stingerLoad.gif)
This result is good news, in the sense that it will save us a total of 2.5 seconds; however, implemented this way, it will block the user interface until the loading is complete. In this case, what we can do is create a separate thread using PyQt’s QThread, which allows us to load the images without blocking the interface.

```python
import os  
import time  
import cv2  
import numpy as np  
from PyQt6.QtCore import *  
from PyQt6.QtGui import *  
from PyQt6.QtWidgets import *

class StingerLoaderThread(QThread):  
   stingerReady = pyqtSignal()  
   progressUpdated = pyqtSignal()

   def __init__(self, _path, parent=None):  
       super().__init__(parent)  
       self.path = _path  
       self.stingerImages = []  
       self.stingerRGBImages = []  
       self.stingerAlphaImages = []  
       self.stingerInvAlphaImages = []  
       self.stingerPreMultipliedImages = []

   def run(self):  
       self.loadStingerFrames(self.path)  
       self._findAlphaInvertAndMerge(self.stingerImages)  
       self._setPremultipliedFrame(self.stingerRGBImages)  
       self.stingerReady.emit()

   def loadStingerFrames(self, _path):  
       for filename in os.listdir(_path):  
           if filename.endswith('.png'):  
               image_path = os.path.join(_path, filename)  
               image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  
               self.stingerImages.append(image)  
               self.progressUpdated.emit()

   def _findAlphaInvertAndMerge(self, imageList):  
       for image in imageList:  
           b, g, r, a = cv2.split(image)  
           a = a / 255.0  
           alpha = cv2.merge((a, a, a))  
           invAlpha = cv2.merge((1 - a, 1 - a, 1 - a))  
           self.stingerAlphaImages.append(alpha)  
           self.stingerInvAlphaImages.append(invAlpha)  
           self.stingerRGBImages.append(cv2.merge((b, g, r)))  
           self.progressUpdated.emit()

   def _setPremultipliedFrame(self, imageList):  
       for image, alpha in zip(imageList, self.stingerAlphaImages):  
           premultiplied = cv2.multiply(image.astype(np.float32), alpha, dtype=cv2.CV_8U)  
           self.stingerPreMultipliedImages.append(premultiplied)  
           self.progressUpdated.emit()

class StingerDisplay(QWidget):  
   def __init__(self, loaderThread, parent=None):

  
       super().__init__(parent)  
       self.loaderThread = loaderThread  
       self.progressBar = QProgressBar(self)  
       self.lbl = QLabel("Loading Stinger Frames...", self)  
       self.timeLabel = QLabel("Time: 0.0s", self)  
       self.timer = QTimer(self)  
       self.startTime = time.time()  
       self.initUI()  
       self.initConnections()  
       self.loaderThread.start()  
       self.timer.start(100)

   def initUI(self):  
       mainLayout = QVBoxLayout()  
       mainLayout.addWidget(self.lbl)  
       mainLayout.addWidget(self.progressBar)  
       mainLayout.addWidget(self.timeLabel)  
       self.setLayout(mainLayout)  
       self.setWindowTitle('Stinger Loader Progress')  
       self.progressBar.setRange(0, 100)

   def initConnections(self):  
       self.loaderThread.progressUpdated.connect(self.updateProgressBar)  
       self.loaderThread.stingerReady.connect(self.onStingerReady)  
       self.timer.timeout.connect(self.animateProgressBar)

   @pyqtSlot()  
   def updateProgressBar(self):  
       pass  # The progress bar is animated by the timer

   @pyqtSlot()  
   def animateProgressBar(self):  
       value = (self.progressBar.value() + 1) % 101  
       self.progressBar.setValue(value)  
       elapsed_time = time.time() - self.startTime  
       self.timeLabel.setText(f"Time: {elapsed_time:.1f}s")

   @pyqtSlot()  
   def onStingerReady(self):  
       self.timer.stop()  
       self.progressBar.setValue(100)  
       elapsed_time = time.time() - self.startTime  
       self.timeLabel.setText(f"Completed in: {elapsed_time:.1f}s")  
       print("All done!")

if __name__ == '__main__':  
   path = r'\\openPyVisionBook\\openPyVisionBook\\cap5\\cap5_5\\stingerTest'  
   stingerLoaderThread = StingerLoaderThread(path)  
   app = QApplication([])  
   stingerDisplay = StingerDisplay(stingerLoaderThread)  
   stingerDisplay.show()

   app.exec()
```

The thread calls various functions via start, with the purpose of filling these lists:

```python
self.stingerImages = []  
self.stingerRGBImages = []  
self.stingerAlphaImages = []  
self.stingerInvAlphaImages = []  
self.stingerPreMultipliedImages = []
```

While writing this code, I encountered various issues. First, we saw that there are faster operations than the ones I used, which we measured in the previous chapter. The problem is that a continuous space in memory is not always created, which, in practical terms, translates into a rapid loading phase, but then a significant slowdown during the matrix multiplication phase.

On GitHub, in the folder for this section, I have left the codes used during this testing phase. The result is that, although counterintuitively and when taken individually, these operations are very fast, the greater speed is due to the lack of memory optimization, which then leads to a slowdown during execution.

```
*Time to load stinger frames: 2.374817371368408 seconds* 
*Time to load stinger frames2: 2.9349265098571777 seconds* 
*Time to load stinger frames3: 2.1785390377044678 seconds* 
*Execution time of stingerFunction3: 4.307186499936506 seconds* 
*Execution time of stingerFunctionFast: 4.3145863998215646 seconds* 
*Execution time of stingerFunction3: 19.326996800024062 seconds*
```

Here's the English translation of the provided text:

---

The first method used `cv2.split` and `cv.merge`, and I expected that using other methods, which individually seemed faster, such as indexing or list comprehensions, would yield better performance. However, for some reason, the same calculation became unexpectedly slower, even though the images appeared identical.

I spent a couple of days trying to understand what was happening behind the scenes, and eventually discovered that the three methods returned three identical arrays, but they were not represented as contiguous in memory. This caused a significant slowdown during the multiplication process.

## **4.6 Stinger More**

Now, we have a stinger class that allows us to access all the precomputed images via an index. What we practically need to do is take the frame, multiply it by the inverse of the alpha, and then add it to the pre-multiplied stinger.

It's always good to remember that if I multiply two `uint8` values together, I will always get an unexpected result because 255 does not give me what the formula strictly shows, which is a multiplication by 1. Therefore, the alpha and inverted alpha have already been normalized in the stinger thread.

```python
def onStingerReady(self):  
   self.frames = self.loaderThread.stingerPreMultipliedImages  
   self.invMasks = self.loaderThread.stingerInvAlphaImages  
   self.timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)

def updateFrame(self):  
   program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)  
   if self.frames:  
       timeStart = time.time()  
       stinger_frame = self.frames[self.currentIndex]  
       inv_mask = self.invMasks[self.currentIndex]  
       program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)  
       result = cv2.add(stinger_frame, program_masked)  
       height, width, channel = result.shape  
       qImg = QImage(result.data, width, height, QImage.Format.Format_BGR888)  
       self.label.setPixmap(QPixmap.fromImage(qImg))  
       self.label.setScaledContents(True)  
       self.label.resize(width, height)  
       self.currentIndex = (self.currentIndex + 1) % len(self.frames)  
       self.lblTime.setText(f"Time: {time.time() - timeStart:.6f}")
```

What we practically need to do is load the pre-multiplied image and the inverted alpha at the current index, then multiply the program by the inverted alpha and add them together.

Unfortunately, this operation exceeds the time we need; it takes about 0.22 seconds, whereas we need it to be completed within 0.016 seconds.

If I have an alpha channel in black and white where the values are either all white or all black, I can use `bitwise_and`, which performs the operation in approximately 0.0022 seconds. The problem is that if the image has feathered edges, the semi-transparent part gets clipped.

Most of an alpha channel, however, is completely transparent only in the worst-case scenario. In most cases, the parts that are neither 0 nor 1 are almost always the majority. This is what the `dtype=cv2.CV_8U` option does: it indicates that I am multiplying a mask by an image, and this image has an 8-bit sRGB color space, which gives me an average execution time of 0.008468 seconds.

```python
class StingerDisplay(QWidget):  
   def __init__(self, loaderThread, parent=None):  
       super().__init__(parent)  
       # Init widgets  
       self.loaderThread = loaderThread  
       self.lblViewer = QLabel(self)  
       self.lblTime = QLabel("Loading Stinger Frames...")  
       self.lblMediaTime = QLabel("Time: 0.0s")  
       self.progressBar = QProgressBar(self)  
       self.vwr_timer = QTimer(self)  
       self.prgBar_timer = QTimer(self)

       # Init variables  
       self.startTime = time.time()  
       self.currentIndex = 0  
       self.totalTimeSpent = 0  
       self.mediaTimeSpend = 0  
       self.mediaIndex = 0  
       self.frames = []  
       self.invMasks = []

       # Init UI  
       self.initUI()  
       self.initGeometry()  
       self.initStyle()  
       self.initConnections()

   def initUI(self):  
       mainLayout = QVBoxLayout()  
       mainLayout.addWidget(self.lblViewer)  
       timeLayout = QHBoxLayout()  
       timeLayout.addWidget(self.lblTime)  
       timeLayout.addWidget(self.lblMediaTime)  
       timeLayout.addWidget(self.progressBar)  
       mainLayout.addLayout(timeLayout)  
       self.setLayout(mainLayout)

   def initConnections(self):  
       self.loaderThread.stingerReady.connect(self.onStingerReady)  
       self.loaderThread.progressUpdated.connect(self.updateProgressBar)  
       self.vwr_timer.timeout.connect(self.updateFrame)  
       self.prgBar_timer.timeout.connect(self.animateProgressBar)  
       self.prgBar_timer.start(100)

   def initStyle(self):  
       lblStyle = ("QLabel {"  
                   "background-color: #000000;"  
                   "color: #00FF00;"  
                   "border: 1px solid #00FF00;"  
                   "border-radius: 5px;}")  
       self.lblViewer.setStyleSheet(lblStyle)

   def initGeometry(self):  
       self.setGeometry(10, 50, 1920, 1080)  
       self.progressBar.setRange(0, 100)

   @pyqtSlot(int)  
   def updateProgressBar(self, value):  
       self.progressBar.setValue(value)

   @pyqtSlot()  
   def animateProgressBar(self):  
       if self.progressBar.value() < 100:  
           value = (self.progressBar.value() + 1) % 101  
           self.progressBar.setValue(value)  
       elapsed_time = time.time() - self.startTime  
       self.lblMediaTime.setText(f"Time: {elapsed_time:.1f}s")

   @pyqtSlot()  
   def onStingerReady(self):  
       self.frames = self.loaderThread.stingerPreMultipliedImages  
       self.invMasks = self.loaderThread.stingerInvAlphaImages  
       self.vwr_timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)  
       self.prgBar_timer.stop()

   def updateFrame(self):  
       program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)  
       if self.frames:  
           timeStart = time.time()  
           stinger_frame = self.frames[self.currentIndex]  
           inv_mask = self.invMasks[self.currentIndex]  
           program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)  
           result = cv2.add(stinger_frame, program_masked)  
           height, width, channel = result.shape  
           qImg = QImage(result.data, width, height, QImage.Format.Format_BGR888)  
           self.lblViewer.setPixmap(QPixmap.fromImage(qImg))  
           self.lblViewer.setScaledContents(True)  
           self.lblViewer.resize(width, height)  
           self.currentIndex = (self.currentIndex + 1) % len(self.frames)  
           self.lblTime.setText(f"Time: {time.time() - timeStart:.6f}")  
           self.updateMediaTime(timeStart)

   def updateMediaTime(self, timeStart):  
       endTime = time.time() - timeStart  
       self.totalTimeSpent += endTime  
       self.mediaIndex += 1  
       self.mediaTimeSpend = self.totalTimeSpent / self.mediaIndex  
       self.lblTime.setText(f"Time: {endTime:.6f}")  
       self.lblMediaTime.setText(f"Media Time: {self.mediaTimeSpend:.6f}")

   def closeEvent(self, event):  
       print(f"Media Time: {self.mediaTimeSpend:.6f}")  
       self.vwr_timer.stop()  
       event.accept()

if __name__ == '__main__':  
   app = QApplication([])

   path = r'/cap5/cap5_5/stingerTest'  
   loaderThread = StingerLoaderThread(path)  
   stingerDisplay = StingerDisplay(loaderThread)  
   stingerDisplay.show()  
   loaderThread.start()

   app.exec()


*Stinger frames loaded in 1.264967 seconds*
*Alpha, Inverted Alpha and RGB frames found in 4.267617 seconds*
*Premultiplied frames found in 1.454782 seconds*
*Total frames: 136*
*Media Time: 0.008719*
```

![][image25]


The result gives us a good average time, but the next question is: can we do better?

To stay under 10 ms per frame (0.010 seconds), the only further optimizations we could consider, if ever needed, might be:

1. **Using a GPU with CUDA or OpenCL** for multiplication and addition operations.
2. **Optimizing the conversion from a NumPy array to QImage** if that part becomes a bottleneck.

The GPU is an interesting topic and one that is increasingly discussed. Unfortunately, I haven't found much literature on how to effectively leverage the graphics card with Python, but we can optimize the transformation from a NumPy array to QImage to display it in the interface with lower cost.

There are various methods to do this, and as usual, the best approach is to have them compete against each other to see which one wins and potentially combine the best aspects of all of them.

A first method that can become common to others is to make the NumPy arrays contiguous in memory because this speeds up calculations.

```python
result = np.ascontiguousarray(result)
qImg = QImage(result.data, width, height, result.strides[0], QImage.Format.Format_BGR888)
```

Avoid copying data: Instead of creating a new QImage for each frame, you can reuse the same QImage and update its data:

```python
class StingerDisplay(QWidget):  
   def __init__(self, loaderThread, parent=None):  
       # ... (existing code) ...  
       self.qImg = QImage(1920, 1080, QImage.Format.Format_BGR888)

   def updateFrame(self):  
       # ... (existing code) ...  
       result = cv2.add(stinger_frame, program_masked)  
       self.qImg.setData(result.data)  
       self.label.setPixmap(QPixmap.fromImage(self.qImg))
```

These first two suggestions can become the basis for what will be our three optimized classes.

## **4.7 STINGER OPTIMIZATION**

The first method involves using a pointer to the data. By using `sip.voidptr`, you can create a pointer to the NumPy array's data without copying the data.

```python
import sip

# ... (in the updateFrame method)  
result = cv2.add(stinger_frame, program_masked)  
ptr = sip.voidptr(result.data)  
qImg = QImage(ptr, width, height, QImage.Format.Format_BGR888)
```

The improvement is small, but it's there, giving us a Media Time of 0.008084 seconds, which is an average saving of 0.000635 seconds.

Another method I found is using `QOpenGLWidget`. If you're doing a lot of image rendering, you might consider switching to `QOpenGLWidget` instead of `QLabel`. This can offer significantly better performance, especially for large images.

```python
from PyQt6.QtOpenGLWidgets import QOpenGLWidget  
from PyQt6.QtGui import QSurfaceFormat

class GLImageWidget(QOpenGLWidget):  
   def __init__(self, parent=None):  
       super().__init__(parent)  
       self.image = QImage()

   def setImage(self, image):  
       self.image = image  
       self.update()

   def paintGL(self):  
       if not self.image.isNull():  
           painter = QPainter(self)  
           painter.drawImage(self.rect(), self.image)  
           painter.end()

class StingerDisplay(QWidget):  
   def __init__(self, loaderThread, parent=None):  
       # ... (existing code) ...  
       self.glWidget = GLImageWidget(self)  
       self.layout.addWidget(self.glWidget)

   def updateFrame(self):  
       # ... (existing code) ...  
       result = cv2.add(stinger_frame, program_masked)  
       qImg = QImage(result.data, width, height, QImage.Format.Format_BGR888)  
       self.glWidget.setImage(qImg)
```

With this optimization, I achieve a Media Time of 0.007786 seconds, which is a saving of 0.000936 seconds compared to the original time.

Another promising method is creating a sort of shared memory using `QSharedMemory`. Since I'm using a `QThread`, this might somehow be helpful.

```python
from PyQt6.QtCore import QSharedMemory

class StingerDisplay(QWidget):  
   def __init__(self, loaderThread, parent=None):  
       # ... (existing code) ...  
       self.shared_memory = QSharedMemory('ImageData')  
       self.shared_memory.create(1920 * 1080 * 3)

   def updateFrame(self):  
       # ... (existing code) ...  
       result = cv2.add(stinger_frame, program_masked)  
       self.shared_memory.lock()  
       memcpy(int(self.shared_memory.data()), result.ctypes.data, result.nbytes)   
       self.shared_memory.unlock()  
       qImg = QImage(self.shared_memory.data(), width, height, QImage.Format.Format_BGR888)  
       self.label.setPixmap(QPixmap.fromImage(qImg))
```

Unfortunately, this method is not very helpful because, from experimental data, I get a Media Time of 0.008373 seconds, which is still better than my starting hypothesis with an improvement of 0.000346 seconds.

Combining the best of these three methods is what I've done in the following code, which gives me an average time of 0.007310 seconds, an average saving of 0.001409 seconds.

```python
import os  
import time  
from PyQt6.QtCore import *  
from PyQt6.QtGui import *  
from PyQt6.QtWidgets import *  
from PyQt6.QtOpenGLWidgets import QOpenGLWidget  
import cv2  
import numpy as np

class StingerLoaderThread(QThread):  
   stingerReady = pyqtSignal()  
   progressUpdated = pyqtSignal(int)  # Signal to update progress with a percentage value  
   somethingDone = pyqtSignal(str, str)

   def __init__(self, _path, parent=None):  
       super().__init__(parent)  
       self.path = _path  
       self.stingerImages = []  
       self.stingerRGBImages = []  
       self.stingerAlphaImages = []  
       self.stingerInvAlphaImages = []  
       self.stingerPreMultipliedImages = []

   def run(self):  
       self.loadStingerFrames(self.path)  
       self._findAlphaInvertAndMerge(self.stingerImages)  
       self._setPremultipliedFrame(self.stingerRGBImages)  
       self.stingerReady.emit()

   def loadStingerFrames(self, _path):  
       startTime = time.time()  
       files = [f for f in os.listdir(_path) if f.endswith('.png')]  
       total_files = len(files)  
       for idx, filename in enumerate(files):  
           image_path = os.path.join(_path, filename)  
           image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  
           self.stingerImages.append(image)  
           self.progressUpdated.emit(int((idx + 1) / total_files * 100))  
       print(f"Stinger frames loaded in {time.time() - startTime:.6f} seconds")  
       returnString = f"Stinger frames loaded in {time.time() - startTime:.6f} seconds"  
       endTime = time.time() - startTime  
       self.somethingDone.emit(returnString, f"{endTime:.6f}")

   def _findAlphaInvertAndMerge(self, imageList):  
       timeStart = time.time()  
       total_images = len(imageList)  
       for idx, image in enumerate(imageList):  
           b, g, r, a = cv2.split(image)  
           a = a / 255.0  
           alpha = cv2.merge((a, a, a))  
           invAlpha = cv2.merge((1 - a, 1 - a, 1 - a))  
           self.stingerAlphaImages.append(alpha)  
           self.stingerInvAlphaImages.append(invAlpha)  
           self.stingerRGBImages.append(cv2.merge((b, g, r)))  
           self.progressUpdated.emit(int((idx + 1) / total_images * 100))  
       returnString = f"Alpha, Inverted Alpha, and RGB frames found in   
                       {time.time() - timeStart:.6f} seconds"  
       endTime = time.time() - timeStart  
       self.somethingDone.emit(returnString, f"{endTime:.6f}")

   def _setPremultipliedFrame(self, imageList):  
       timeStart = time.time()  
       total_images = len(imageList)  
       for idx, (image, alpha) in enumerate(zip(imageList, self.stingerAlphaImages)):  
           premultiplied = cv2.multiply(image.astype(np.float32),   
                                        alpha, dtype=cv2.CV_8U)  
           self.stingerPreMultipliedImages.append(premultiplied)  
           self.progressUpdated.emit(int((idx + 1) / total_images * 100))  
       returnString = f"Premultiplied frames found in   
                       {time.time() - timeStart:.6f} seconds"  
       endTime = time.time() - timeStart  
       self.somethingDone.emit(returnString, f"{endTime:.6f}")

       print(f"Total frames: {len(self.stingerPreMultipliedImages)}")

class GLImageWidget(QOpenGLWidget):  
   def __init__(self, parent=None):  
       super().__init__(

parent)  
       self.image = QImage()

   def setImage(self, image):  
       self.image = image  
       self.update()

   def paintGL(self):  
       if not self.image.isNull():  
           painter = QPainter(self)  
           painter.drawImage(self.rect(), self.image)  
           painter.end()

class StingerDisplay(QWidget):  
   floatCount = 0

   def __init__(self, _loaderThread, parent=None):  
       super().__init__(parent)  
       # init widgets  
       self.loaderThread = _loaderThread  
       self.glWidget = GLImageWidget(self)  
       self.lblTime = QLabel("Time: 0.0")  
       self.lblMediaTime = QLabel("Media Time: 0.0")  
       self.prgBar = QProgressBar(self)  
       self.timer = QTimer(self)  
       self.prgBar_timer = QTimer(self)  
       # init variables  
       self.startTime = time.time()  
       self.currentIndex = 0  
       self.totalTimeSpent = 0  
       self.mediaTimeSpend = 0  
       self.mediaIndex = 0  
       self.frames = []  
       self.invMasks = []  
       self.qImg = QImage(1920, 1080, QImage.Format.Format_BGR888)  
       # init UI  
       self.initUI()  
       self.initGeometry()  
       self.initStyle()  
       self.initConnections()

   def initUI(self):  
       mainLayout = QVBoxLayout()  
       mainLayout.addWidget(self.glWidget)  
       timeLayout = QHBoxLayout()  
       timeLayout.addWidget(self.lblTime)  
       timeLayout.addWidget(self.lblMediaTime)  
       timeLayout.addWidget(self.prgBar)  
       mainLayout.addLayout(timeLayout)  
       self.setLayout(mainLayout)

   def initStyle(self):  
       lblStyle = ("QLabel {"  
                   "background-color: #000000;"  
                   "color: #00FF00;"  
                   "border: 1px solid #00FF00;"  
                   "border-radius: 5px;}")  
       self.glWidget.setStyleSheet(lblStyle)  
       self.prgBar.setMaximum(100)

   def initGeometry(self):  
       self.setGeometry(0, 0, 1920, 1080)  
       self.setWindowTitle('Stinger Display')  
       self.glWidget.setFixedSize(1920, 1080)

   def initConnections(self):  
       self.loaderThread.stingerReady.connect(self.onStingerReady)  
       self.loaderThread.progressUpdated.connect(self.updateProgressBar)  
       self.loaderThread.somethingDone.connect(self.updateProgressBarText)  
       self.timer.timeout.connect(self.updateFrame)  
       self.prgBar_timer.timeout.connect(self.animateProgressBar)  
       self.prgBar_timer.start(100)

   @pyqtSlot(int)  
   def updateProgressBar(self, value):  
       self.prgBar.setValue(value)

   @pyqtSlot()  
   def animateProgressBar(self):  
       if self.prgBar.value() < 100:  
           value = (self.prgBar.value() + 1) % 101  
           self.prgBar.setValue(value)  
       elapsed_time = time.time() - self.startTime  
       self.lblMediaTime.setText(f"Time: {elapsed_time:.1f}s")

   @pyqtSlot(str, str)  
   def updateProgressBarText(self, returnString, timeString):  
       print(f"{returnString} in {timeString} seconds")  
       self.floatCount += float(timeString)  
       if self.prgBar.value() >= 100:  
           self.prgBar.setValue(100)  
           self.prgBar_timer.stop()

   @pyqtSlot()  
   def onStingerReady(self):  
       self.frames = self.loaderThread.stingerPreMultipliedImages  
       self.invMasks = self.loaderThread.stingerInvAlphaImages  
       self.timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)  
       self.prgBar_timer.stop()

   def updateFrame(self):  
       program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)  
       if self.frames:  
           timeStart = time.time()  
           stinger_frame = self.frames[self.currentIndex]  
           inv_mask = self.invMasks[self.currentIndex]  
           program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)  
           result = cv2.add(stinger_frame, program_masked)  
           result_contiguous = np.ascontiguousarray(result)               
           height, width, channel = result_contiguous.shape  
           self.qImg = QImage(result_contiguous.data, width, height,  
                              QImage.Format.Format_BGR888)  
           self.glWidget.setImage(self.qImg)  
           self.currentIndex = (self.currentIndex + 1) % len(self.frames)  
           self.updateMediaTime(timeStart)

   def updateMediaTime(self, timeStart):  
       endTime = time.time() - timeStart  
       self.totalTimeSpent += endTime  
       self.mediaIndex += 1  
       self.mediaTimeSpend = self.totalTimeSpent / self.mediaIndex  
       self.lblTime.setText(f"Time: {endTime:.6f}")  
       self.lblMediaTime.setText(f"Media Time: {self.mediaTimeSpend:.6f}")

   def closeEvent(self, event):  
       print(f"Media Time: {self.mediaTimeSpend:.6f}")  
       self.timer.stop()  
       event.accept()

if __name__ == '__main__':  
   app = QApplication([])  
   path = r'\\openPyVisionBook\\openPyVisionBook\\cap5\\cap5_5\\stingerTest'  
   loaderThread = StingerLoaderThread(path)  
   stingerDisplay = StingerDisplay(loaderThread)  
   stingerDisplay.show()  
   loaderThread.start()  
   app.exec()
```

## **4.8 STINGER IN THE MIXBUS**

Obviously, our goal at this point is to insert the stinger into the mixbus so that we have it along with the other effects. We need to write some code:

```python
def stinger(self, preview_frame, program_frame):  
   stinger_frame = self.stinger_frames[self._wipe]  
   inv_mask = self.stinger_invMasks[self._wipe]

   if self._wipe < len(self.stinger_frames) // 2:  
       program_masked = cv2.multiply(program_frame, inv_mask,  
                                     dtype=cv2.CV_8U)  
       result = cv2.add(stinger_frame, program_masked)  
       return np.ascontiguousarray(result)  
   else:  
       preview_masked = cv2.multiply(preview_frame, inv_mask,  
                                     dtype=cv2.CV_8U)  
       result = cv2.add(stinger_frame, preview_masked)  
       return np.ascontiguousarray(result)
```

What happens is that `_wipe` will be the index of the stinger list. When the stinger loader class has finished all the operations, the code initializes the two lists. The timer starts with automix, and as long as we're before the middle of the list, the operation will be done with the program. Usually, around the middle, the stinger completely covers the screen, and at this point, we switch the program with the preview.

```python
def _fader(self):  
   if self.effectType == MIX_TYPE.FADE:  
       self._fade += 0.01  
       if self._fade > 1:  
           self.autoMix_timer.stop()  
           self.cut()  
   elif self.effectType in   
             [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT,  
               MIX_TYPE.WIPE_TOP_TO_BOTTOM, MIX_TYPE.WIPE_BOTTOM_TO_TOP]:

       self._wipe += 1  
       self._fade += 0.01  
       if self._wipe > len(self._wipe_position_leftToRight_list) - 1:  
           self.autoMix_timer.stop()  
           self.cut()  
   elif self.effectType == MIX_TYPE.WIPE_STINGER:  
       self._wipe += 1  
       self._fade += 0.01  
       if self._wipe > len(self.stinger_frames) - 1:  
           self.autoMix_timer.stop()  
           self.cut()
```

We have also seen that instead of Qt's labels, it is much more convenient to create a viewer that we partially wrote in the previous example.

```python
from PyQt6.QtGui import QImage, QPainter  
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

class OpenGLViewer(QOpenGLWidget):  
   def __init__(self, parent=None):  
       super().__init__(parent)  
       self.image = QImage()

   def setImage(self, image):  
       self.image = image  
       self.update()

   def paintGL(self):  
       if not self.image.isNull():  
           painter = QPainter(self)  
           painter.drawImage(self.rect(), self.image)  
           painter.end()
```

Now all that's left is to create the `testMixBus5_8` class to test the new mixbus. We can then add the stinger to the list of effects, use `OpenGLViewer` instead of labels, and even use the example from chapter 5_5—remember? The widget with the progress bar indicating how much time is left for

 loading, giving the user a timing.

```python
class testMixBus4_8(QWidget):  
   def __init__(self, synchObject, loaderThread, parent=None):  
       super().__init__(parent)  
       self.syncObject = synchObject  
       self.input1 = ColorGenerator(self.syncObject)  
       self.input2 = RandomNoiseGenerator(self.syncObject)  
       self.mixBus = MixBus5_8(self.input1, self.input2, loaderThread)  
       self.previewViewer = OpenGLViewer()  
       self.programViewer = OpenGLViewer()  
       self.btnCut = QPushButton("CUT")  
       self.btnAutoMix = QPushButton("AutoMix")  
       self.sldFade = QSlider()  
       self.cmbEffect = QComboBox()  
       self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left",  
                                "Wipe Top to Bottom", "Wipe Bottom to Top", "Stinger"])  
       self.sldFade.setOrientation(Qt.Orientation.Horizontal)  
       self.sldFade.setRange(0, 100)  
       self.initUI()  
       self.initGeometry()  
       self.initConnections()

   def initUI(self):  
       mainLayout = QVBoxLayout()  
       viewerLayout = QHBoxLayout()  
       viewerLayout.addWidget(self.previewViewer)  
       viewerLayout.addWidget(self.programViewer)  
       spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)  
       buttonLayout = QHBoxLayout()  
       buttonLayout.addItem(spacer)  
       buttonLayout.addWidget(self.btnCut)  
       buttonLayout.addWidget(self.btnAutoMix)  
       buttonLayout.addWidget(self.sldFade)  
       buttonLayout.addWidget(self.cmbEffect)  
       mainLayout.addLayout(viewerLayout)  
       mainLayout.addLayout(buttonLayout)  
       self.setLayout(mainLayout)

   def initGeometry(self):  
       self.previewViewer.setFixedSize(640, 360)  
       self.programViewer.setFixedSize(640, 360)

   def initConnections(self):  
       self.syncObject.synch_SIGNAL.connect(self.updateFrame)  
       self.btnCut.clicked.connect(self.cut)  
       self.btnAutoMix.clicked.connect(self.autoMix)  
       self.sldFade.valueChanged.connect(self.setFade)  
       self.cmbEffect.currentIndexChanged.connect(self.setEffect)

   def updateFrame(self):  
       prw_frame, prg_frame = self.mixBus.getMixed()  
       prw_frame = cv2.resize(prw_frame, (640, 360))  
       prg_frame = cv2.resize(prg_frame, (640, 360))  
       prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)  
       prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)  
       self.previewViewer.setImage(prw_image)  
       self.programViewer.setImage(prg_image)

   def cut(self):  
       self.mixBus.cut()

   def autoMix(self):  
       self.mixBus.autoMix()

   def setFade(self):  
       self.mixBus.setFade(self.sldFade.value())

   def setEffect(self):  
       effect = self.cmbEffect.currentText()  
       if effect == "Fade":  
           self.mixBus.effectType = MIX_TYPE.FADE  
       elif effect == "Wipe Left to Right":  
           self.mixBus.effectType = MIX_TYPE.WIPE_LEFT_TO_RIGHT  
       elif effect == "Wipe Right to Left":  
           self.mixBus.effectType = MIX_TYPE.WIPE_RIGHT_TO_LEFT  
       elif effect == "Wipe Top to Bottom":  
           self.mixBus.effectType = MIX_TYPE.WIPE_TOP_TO_BOTTOM  
       elif effect == "Wipe Bottom to Top":  
           self.mixBus.effectType = MIX_TYPE.WIPE_BOTTOM_TO_TOP  
       elif effect == "Stinger":  
           self.mixBus.effectType = MIX_TYPE.WIPE_STINGER

if __name__ == '__main__':  
   import sys  
   app = QApplication(sys.argv)  
   path = r'\\openPyVisionBook\\openPyVisionBook\\cap5\\cap5_5_StingerIdea\\stingerTest'  
   loaderThread = StingerLoaderThread(path)  
   synchObject = SynchObject()  
   stingerDisplay = StingerDisplay(loaderThread)  
   stingerDisplay.show()  
   test = testMixBus5_8(synchObject, loaderThread)  
   test.show()  
   sys.exit(app.exec())
```
