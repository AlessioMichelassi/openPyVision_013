

# 2: The Al Jabr of Images
### 2.1 A Gentle Introduction

The mathematics behind video is not difficult to understand, but it has its complexities and requires resources at the hardware level. To fully understand how a video mixer works, we will start by defining how computers perceive images and how they can sum and multiply them together. This will lead us directly to the heart of the problem: execution speed.
### 2.1.1 The Matrix

In computer science, image processing is a discipline known as Computer Generated Imagery (CGI). A color image can be represented as a matrix of pixels, where each pixel is a vector of three RGB (red, green, blue) values. Each pixel has a value ranging from 0 to 1; 0 indicates the absence of color, and 1 represents the maximum presence of color.

In simpler terms, we can say that a color image is composed of three matrices: one for green, one for red, and one for blue. We can visualize these matrices with an 8x8 pixel example:
Zero represents black, while 1 represents white. 0.5 is the medium gray. With this system, we can create black-and-white images—three to be precise—each representing the amount or map of red, green, and blue present in the image.

The first fact is that in computers, there are no color images, only matrices of numbers. The task of creating color from these values is handled by the devices to which we send this information. Inside computers, every single image is a matrix, and each point that defines it is called a pixel, represented by three values ranging from 0 to 1. Whether we consider an RGB vector or three matrices is just a formal way of naming it.

The second fact is that numbers inside computers do not actually exist. They are represented using a system called discretization. This means that the values are divided into discrete units, or steps, that the computer can manipulate. Computers use a binary system, consisting only of 0s and 1s, called bits (binary digits). These bits are combined to store and manipulate all kinds of data, including numbers and text.

To understand how integers are created, we can imagine a memory space consisting of 8 cells (or bits), each of which can be either 0 or 1. This is known as a byte.
```
|0|0|0|0|0|0|0|0| = 0
|0|0|0|0|0|0|0|1| = 1
|0|0|0|0|0|0|1|0| = 2
|0|0|0|0|0|0|1|1| = 3
...
|1|1|1|1|1|1|1|0| = 254
|1|1|1|1|1|1|1|1| = 255
```
Thus, a byte is the set of 8 cells or bits that contain a value from 0 to 1, and this block of bits is called a register. In this system, 0 represents black, and 255 represents white, while 127 is medium gray. Computers no longer have 8-bit registers for more than 20 years; currently, registers are 64-bit, but there are also 256-bit and even 512-bit registers. Although it may seem a bit limiting to use only 8 bits to represent color, we can say that Photoshop, for example, uses 16 bits to give the user the ability to achieve the highest image quality.

The pioneers who first asked these questions were probably researchers at Kodak. Even though film continued to be considered a constant, they understood that there was a future in digitizing images to create visual effects, restore films, and perform color correction using computers. While 8 bits were too few and 16 bits were too many, they found alternative systems, such as using 10 bits.

However, the trend over the years has always been to reduce file sizes because hard drives are sold by the euro/byte. Here is an example of the difference in file sizes:

 * A 1920x1080 image at 8 bits occupies about 6.2 MB.
 * A 1920x1080 image at 10 bits occupies about 7.75 MB.
 * A 1920x1080 image at 16 bits occupies about 12.44 MB.

In the case of a 60 frames-per-second video, we must multiply everything by 60, which gives us:
 * 6.2 MB * 60 = 372 MB per second for an 8-bit video.
 * 7.75 MB * 60 = 465 MB per second for a 10-bit video.
 * 12.44 MB * 60 = 746.4 MB per second for a 16-bit video.

An interesting document is the one published in 1995 by Kodak for 10-bit to 8-bit conversion, where it explained to technicians how to convert 10-bit images from film format to 8-bit video. Kodak Cineon Document[cineon](https://www.dotcsw.com/doc/cineon1.pdf).

Cineon was a digitization system developed by Kodak in the 1990s for film post-production. It included both the hardware and software needed for scanning film and converting it to digital format. It was introduced commercially for production companies in the 1990s and was a system designed to maintain high quality during the digitization process, allowing post-production to be done in digital format and then retransfer the footage onto film for distribution. This process is known as "Digital Intermediate."

### 2.1.3 The Utility of the Normalization System

So, OK. 255 is white at 8 bits, if it's at 16 bits, it becomes 65535, but as mentioned, there are 10-bit color spaces (1024) and sometimes 12-bit (4096). Thus, if white and medium gray always have different values, it becomes extremely easy to get confused and make mistakes. To solve this problem, the normalization system is used.

Data normalization allows you to say that regardless of the color resolution or bit depth of the system, 0 is black, and 1 is white. Therefore, if I have a 10-bit image, I don't have to get confused in making calculations because white is 1024; it simply remains 1. This approach facilitates the implementation of image processing algorithms in a consistent and scalable manner.

In Python, we can use the NumPy library (which will be discussed in more detail in Chapter 3) to work with matrices and create images. NumPy is a powerful library that allows you to perform vector and matrix operations efficiently, making it ideal for image manipulation. When I create a matrix, I have to declare in advance what its shape and bit depth will be.

The simplest color space to understand is sRGB, which has an 8-bit depth. To create a simple image, we can use NumPy to generate a matrix of values. Here is an example of code that creates a random image:


```python
import numpy as np
import matplotlib.pyplot as plt

height = 8
width = 8

# Create a matrix with 3 channels r,g,b at 8 bits
image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

# Display the image
plt.figure(figsize=(10, 6))  # Set the figure size
plt.imshow(image)
plt.axis('off')  # Hide the axes
plt.title('Random Color Image')
plt.show()

```
NumPy allows us to create images, and matplotlib displays them super easily. In this case, we create a matrix with random values inside. We visualized it, but we can also print it simply by writing print(image).

We will delve into NumPy later in the text, while we will pretend to already know what the 4 matplotlib commands we are using do because we will mainly use them to quickly visualize simple black-and-white and color images. The beauty of NumPy is that it allows us to see what's inside an image simply by using the print command.

```python
image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
print(image)

[[[ 58 253 158]
  [ 14 184 121]
  [235 165 140]
  [134 134 110]
  [148 118 192]
  [ 48 255  64]
  [ 57 238 180]
  [186 113 183]]
```

In the print, we can see the data of the RGB matrices that NumPy groups in a somewhat peculiar way. Is this the representation that NumPy uses to accelerate calculations?
However, using this script, we can have fun visually representing the data present in the three matrices in the way we would expect to see them.

```python
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

height = 8
width = 8

# Create a matrix with 3 channels r,g,b at 8 bits
image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)

# Extract the red, green, and blue channels
green_channel = image[:, :, 1]
red_channel = image[:, :, 0]
blue_channel = image[:, :, 2]

# Create pandas dataframes to visualize the matrices
df_green = pd.DataFrame(green_channel)
df_red = pd.DataFrame(red_channel)
df_blue = pd.DataFrame(blue_channel)

# Print the matrices
print("GREEN")
print(df_green)
print("\nRED")
print(df_red)
print("\nBLUE")
print(df_blue)

# Visualize the image with matplotlib
plt.figure(figsize=(10, 6))
plt.imshow(image)
plt.axis('off')
plt.title('Random Color Image')
plt.show()

```

```plaitext
GREEN                                             RED                                             BLUE                                       
    0    1    2    3    4    5    6    7              0    1    2    3    4    5    6    7            0    1    2    3    4    5    6    7  
0  173   51  183   21  102  160  184  165         0  205    8  185  239  156  185   44  205       0  254  107  112   66  236  195  115  165  
1  179   99  165   86   65  191   96  174         1  204  254  201  220  106  242   35  125       1  235  151   63   83  222   69  113   45  
2  222   81  227   65   81  201  158  252         2   93  200  238  103   85  214  250   21       2   76   67   90  114  180   21  159   33  
3  184  127  102   42   50  174  247  122         3  126   54  213  158  228  160   71   49       3  161  174  135  188  209  106  251  202  
4  166  196  168  113    8  250  148  186         4  241   27   61   51  125  117  245   75       4  108   37   59  108  171  116   22  108  
5  250  254   21   46  211   37   52  174         5  157  170  218  115  141   75  245   47       5   40   67   57   85  145  116  132  177
6  182  223   72  237  175  237  211  253         6  120  157   40  120    5   87  203  192       6   95   85  109  118   74   53  255  118
7  157   59  189  163  142  236   39  101         7  197  245  200  145  235  203  161  243       7  113  216   69  222   31  163  134  123

```
### 2.2 - CIE and Standardization

sRGB is an 8-bit color space and is still considered a widely used and popular standard. It is based on a study called CIE 1931. The CIE, or Commission Internationale de l'Éclairage (International Commission on Illumination), is an international organization responsible for standardization in the fields of light, lighting, color, and color spaces. Founded in 1913, the CIE is the main international authority on light, lighting, color, and color spaces. Its primary purpose is to standardize and provide measurement procedures in the field of lighting and color.

The CIE color spaces were created using data from a series of experiments in which human test subjects adjusted the primary colors red, green, and blue to find a visual match to a second pure color. The original experiments were conducted in the mid-1920s and have continued over time in an attempt to simplify the mathematics behind the scenes.

The chart essentially shows us the entire visual spectrum with two triangles representing the sRGB space and the 16-bit space proposed by Adobe with Photoshop. The Adobe RGB space is larger and more similar, but not identical, to what a human being can perceive. However, various physicists studying the matter noticed how visual perception is deceived by a series of factors known as optical illusions. For this reason, the sRGB system continues to be widely used.

You can delve into optical or visual illusions in this section of Wikipedia: [Optical Illusion](https://en.wikipedia.org/wiki/Optical_illusion).

sRGB, among other things, will help us simplify the calculations in our examples and implementations. This is particularly relevant for internet streaming, where the codecs used for transmission generally operate at 8 bits.

### 2.3 - The I/O Graph

When I was studying special effects, there were two books considered fundamental, at least by those who taught me the subject, who often described them as the Bible and the Gospel of the field. The first is The Art and Science of Digital Compositing by Ron Brinkman, the author of the "Shake" software. The second is Digital Compositing for Film and Video by Steve Wright, a veteran of the special effects industry.

Both show that it is possible to create a graph called I/O (Input/Output) where the X and Y axes represent the values of the image before and after the modification. Suppose 0 represents the unmodified image and 1 represents the completely modified image. We will then have a straight line that goes from (0,0) to (1,1) if the image has not been modified in any way.

We can build a Python script to show what happens to an image each time we modify it with a certain operation.
```python
import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt

class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Graph Widget')
        self.setGeometry(100, 100, 400, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Enter the operation (e.g., *1.2, +0.4, (x-0.33)*3)")
        self.input_box.textChanged.connect(self.update_graph)
        self.layout.addWidget(self.input_box)

        self.graph_widget = GraphDrawingWidget()
        self.layout.addWidget(self.graph_widget)

    def update_graph(self, text):
        self.graph_widget.update_curve(text)

class GraphDrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)

        # Define colors
        self.gridColor = QColor(200, 200, 200)
        self.axisColor = QColor(255, 0, 0)
        self.lineColor = QColor(0, 0, 0)
        self.dotLineColor = QColor(155, 155, 155)
        self.textColor = QColor(0, 0, 255)
        self.expression = 'x'
        self.curve = np.linspace(0, 1, 100)
        self.update_curve(self.expression)

    def update_curve(self, expression):
        self.expression = expression
        x = np.linspace(0, 1, 100)
        try:
            y = eval(self.expression)
            self.curve = np.clip(y, 0, 1)
        except Exception as e:
            self.curve = x  # If there's an error, revert to the identity curve
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # Draw the grid
        painter.setPen(QPen(self.gridColor, 1, Qt.PenStyle.SolidLine))
        for x in range(0, self.width(), 20):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 20):
            painter.drawLine(0, y, self.width(), y)

        # Draw the axes
        painter.setPen(QPen(self.axisColor, 2, Qt.PenStyle.SolidLine))
        painter.drawLine(50, self.height() - 50, self.width() - 50, self.height() - 50)  # X axis
        painter.drawLine(50, self.height() - 50, 50, 50)  # Y axis

        # Draw labels and ticks
        painter.setPen(QPen(self.textColor, 2))
        painter.setFont(painter.font())
        painter.drawText(self.width() - 50, self.height() - 30, 'INPUT')
        painter.drawText(10, 40, 'OUTPUT')
        painter.drawText(35, self.height() - 55, '0')
        painter.drawText(self.width() - 60, self.height() - 55, '1')
        painter.drawText(35, (self.height() - 50) // 2 + 15, '0.5')
        painter.drawText((self.width() - 50) // 2, self.height() - 30, '0.5')

        # Draw the curve
        painter.setPen(QPen(self.lineColor, 2, Qt.PenStyle.SolidLine))
        for i in range(1, len(self.curve)):
            start_x = 50 + (self.width() - 100) * (i - 1) / (len(self.curve) - 1)
            end_x = 50 + (self.width() - 100) * i / (len(self.curve) - 1)
            start_y = self.height() - 50 - (self.height() - 100) * self.curve[i - 1]
            end_y = self.height() - 50 - (self.height() - 100) * self.curve[i]
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

        # Draw dashed lines
        pen = QPen(self.dotLineColor, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(50, 50, self.width() - 50, 50)  # Line from (0,1) to (1,1)
        painter.drawL

```

### **2.4 - Simple Operations**

By multiplying all the pixels by a value, for example, 1.5, you increase the brightness of the image. This operation is called "Gain." Mathematically:

y=x×gain 

Where **`x`** is the initial pixel value and **`gain`** is the multiplication factor. When we look at the graph, we see that the line increases its slope, reflecting the increase in brightness. However, all pixel values are capped at a maximum of 1, so if an operation produces a value greater than 1, it is reduced to 1, a phenomenon called "clamping." The same happens for values that fall below zero. This effect is more noticeable when the color resolution (or "exposure latitude" in the days of film) is limited. However, the detail in the darker parts of the image is preserved since values close to zero remain similar.

The "Brightness" operation, similar to "Gain," involves adding a constant value to all the pixels in the image:

 y=x+brightness

 In this case, the line in the graph shifts upward, clearly showing clamping both at the top and bottom.

One of the most commonly used operations to enhance an image is changing the contrast, which represents the difference between the lightest and darkest parts of the image. Increasing the contrast makes the darker areas darker and the brighter areas brighter.

Conversely, decreasing it reduces the brightness of the bright areas and makes the dark areas lighter. There is no universal standard for how a contrast operator should be implemented. One method, as shown by Ron Brinkman in his "The Art & Science of Digital Compositing," is to subtract a constant value and then multiply the result by another constant:

y=(x−0.33)×3

Again, there is clamping, but if the image is improved and does not have significant losses, this is a fast system that allows you to work on the image with sum and multiplication operations.

The ideal is to soften the edges so that the graph takes on an "S" shape. This type of contrast is called polarized or "biased." In addition to keeping all the data within the domain, it significantly improves the final result:

y=1/(1+exp(−10×(x−0.5)))​

Don't worry if it looks difficult; we will see that there are algorithms to calculate this very quickly and easily.

Gamma correction is another fundamental operation in image processing:

y=x^(1/gamma)

where **`y`** is the output, **`x`** is the input, and **`gamma`** is the correction factor. With a calculator, it is easy to verify how different gamma values correspond to different brightness levels for each pixel. For example, a pixel with an initial value of 0.5 will end up with a value of about 0.665 if we use a gamma of 1.7. The real reason for the popularity of the gamma operator becomes evident when you examine what happens to the extreme values, i.e., 0 and 1, of the image. In other words, "Gamma Correction" only affects non-white or non-black pixels, increasing brightness without clamping the pixels.

Another useful operation is color inversion. By multiplying an image by -1 and subtracting 1, you get the negative:

y=1−x

In film, some operations were done using the negative and then turning it into a positive. Some mathematical expressions are nothing more than the transposition of what was done in the lab.

To understand how to apply these operations to images, we need to delve into how images are handled, and we can do this very simply using NumPy.

## **2.5 - NUMPY**

[**NumPy**](https://numpy.org/) is a fundamental package for scientific computing in Python. It is installed using the command **`pip install numpy`** and is an external library that allows you to work with multidimensional arrays such as vectors and matrices. NumPy offers a wide range of routines for fast operations on arrays, including mathematical, logical, shape manipulation, sorting, selection, I/O, discrete Fourier transforms, basic linear algebra, basic statistical operations, random simulations, and more.

It was originally created by Travis Oliphant in 2005 as an extension of the *Numeric* library to provide a more powerful and flexible framework for numerical computing. Since then, it has become one of the most widely used tools in the scientific and data science community.

Before showing how fast NumPy is, let's see what it offers and how it can be used to create images.
```python
import numpy as np

blackFrame = np.zeros((1080, 1920, 3), dtype=np.uint8)
```
The **`np.zeros`** command creates a matrix of zeros with the specified dimensions. In this case, we create a 1080x1920 matrix with 3 channels (red, green, and blue) and assign the data type **`uint8`**, which represents an unsigned 8-bit integer (positive values between 0 and 255).

```python
# use matplotlib to show the image
import matplotlib.pyplot as plt

plt.imshow(blackFrame)
plt.show()
```

The **`np.ones`** command creates a matrix of 1s with the specified dimensions. We multiply by 255 to get a completely white frame.
```python
# Create a black frame with dimensions 1080x1920 and 3 channels (RGB)
oneFrame = np.ones((1080, 1920, 3), dtype=np.uint8) * 255
```
Another option to achieve the same result is **`np.full`**, which creates a matrix of the specified size filled with the value 255.
```python
# Create a white frame
whiteFrame = np.full((1080, 1920, 3), 255, dtype=np.uint8)
```
The **`np.random.randint`** command generates random integers in the specified range (0-255) to create a frame with random noise.
```python
# Create a frame with random noise
randomFrame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
```
**`np.linspace`** allows you to create a list of evenly spaced numbers. For example, to create a gradient that goes from zero to 255:
```python
import numpy as np
import matplotlib.pyplot as plt

# Horizontal gradients
gradient_h = np.linspace(0, 255, 1920, dtype=np.uint8)
gradient_h = np.tile(gradient_h, (1080, 1))

plt.imshow(gradient_h, cmap='gray')
plt.title('Horizontal Gradient')
plt.show()
```
First, we create a series of linear values between 0 and 255 and then stack the series using tile, which creates 1080 repetitions.

The same thing can be done vertically.
```python
gradient_v = np.linspace(0, 255, 1080, dtype=np.uint8)
gradient_v = np.tile(gradient_v, (1920, 1)).T
```
In this case, the image is created vertically, and then once the values are stacked, the matrix is transposed to change its shape from 1080x1920 to 1920x1080.

**`np.logspace`** does the same thing but creates a series of logarithmic values:
```python
import numpy as np
import matplotlib.pyplot as plt

# Create a logarithmic intensity map
log_space = np.logspace(0, 2, 1920, dtype=np.float32)
log_space = np.tile(log_space, (1080, 1))

plt.imshow(log_space, cmap='gray', norm=plt.Normalize(vmin=log_space.min(), vmax=log_space.max()))
plt.title('Logarithmic Pattern')
plt.show()
```

Here's the translation of your text into English:

---

### **2.5.2 - NUMPY SLICE**

NumPy has a system for manipulating arrays similar to what we use with Python, for example, in lists, called slicing.

array\[start:stop:step\]

Slices allow you to access and modify subsets of arrays without creating unnecessary copies of the data, making the code faster and more readable.

If **`start`** is omitted, the array starts from the first element; **`stop`** indicates the last element, while **`step`** indicates the step between each element (by default, it is 1). **`[: : 2]`** means from the first to the last, every two.

For example:

```python
# Create an 8x8 white matrix
whiteMat = np.ones((8, 8), dtype=np.uint8) * 255

# Create an 8x8 black matrix
blackMat = np.zeros((8, 8), dtype=np.uint8)

# Create an empty 8x8 image (to hold half of one and half of the other)
combinedMat = np.zeros((8, 8), dtype=np.uint8)

# Combine the two matrices
combinedMat[:, :4] = whiteMat[:, :4]
combinedMat[:, 4:] = blackMat[:, 4:]

# Display the combined image
plt.imshow(combinedMat, cmap='gray')
plt.title('Half White and Half Black')
plt.show()
```

The operation **`[:, :4]`** selects all rows and the first 4 columns of the array.

When talking about slicing, it might be useful to remember that the first element is 0 and the second is 1. Sometimes this can be confusing, especially when working with matrices. For example, **`array[0, 0]`** accesses the element in the first row and first column, while **`array[1, 2]`** accesses the element in the second row and third column.

Another way to use slicing is to insert a comma instead of the stop. In this case, you specify a two-dimensional slice **`[rowStart:rowStop, colStart:colStop]`**. It is a bit counterintuitive because, in this case, you indicate the number of rows and columns instead of the position. For example, **`array[:, 4:]`** selects all rows and columns from the fourth onward.

These two methods may seem similar in writing, but it is important not to confuse them: one is used to access specific elements, while the other is used to select ranges of rows and columns.

Later, we will see how this allows us to perform a wipe fade between two images. For now, let's limit ourselves to creating an E.B.U. (European Broadcast Union) color bars generator.

```python
from matplotlib import pyplot as plt
import numpy as np

colors = [
   (192, 192, 192),  # Gray
   (192, 192, 0),    # Yellow
   (0, 192, 192),    # Cyan
   (0, 192, 0),      # Green
   (192, 0, 192),    # Magenta
   (192, 0, 0),      # Red
   (0, 0, 192),      # Blue
   (0, 0, 0)         # Black
]

width, height = 1920, 1080
# Create an empty matrix
bar_height = height
bar_width = width // len(colors)
bars = np.zeros((bar_height, width, 3), dtype=np.uint8)

# Fill each section with the corresponding color
for i, color in enumerate(colors):
   bars[:, i * bar_width:(i + 1) * bar_width, :] = color

plt.imshow(bars)
plt.title('Colored Bars')
plt.show()
```

**`np.arange`** is a NumPy function that generates an array containing equally spaced values within a specified range. It is similar to Python's **`range`** function but returns a NumPy array instead of a range object.

### *numpy.arange(\[start, \]stop, \[step, \]dtype=None, \*, device=None, like=None)*

Where *start (optional)* is the beginning of the interval and defaults to 0, *stop* is the end of the interval - *The interval does not include this value* - *step* (optional) is the spacing between values (default is 1), and *dtype* (optional) is the data type of the resulting array. If not specified, the data type is inferred from the other arguments.

*Device* (optional) is the device on which to place the created array. Default: None, while *like* (optional) is a reference object to allow the creation of arrays that are not NumPy arrays.

```python
import numpy as np
import matplotlib.pyplot as plt
arr = np.arange(0, 1920, dtype=np.uint8)
arr = np.tile(arr, (1080, 1))
print(arr)
print(arr.shape)
print(arr.dtype)
print(arr.min(), arr.max())

plt.imshow(arr, cmap='gray')
plt.show()
```

In this example, you would expect to see a gradient. However, since **`uint8`** ranges from 0 to 255, the values "wrap around" to 0, causing repetitions instead of a continuous gradient. This can still be useful for creating regular patterns.

Here is an example of creating an 8x8 grid with vertical bars using **`np.arange`**:

```python
import numpy as np
import matplotlib.pyplot as plt

# Create an 8x8 grid with vertical bars
bar_height = 8
bar_width = 8

# Create an array of column indices
columns = np.arange(bar_width)

# Alternate between white (255) and black (0) columns
bars = (columns % 2) * 255

# Repeat the vertical bars across all rows
bars = np.tile(bars, (bar_height, 1))

plt.imshow(bars, cmap='gray')
plt.title('Vertical Bars')
plt.show()
```

**`np.mgrid`** is a very useful tool for creating multidimensional mesh grids, which are essentially coordinates in a multidimensional space. This can be particularly useful for graphics, visualization, and creating regular patterns or grids of points. Here is an example to create a circular pattern:

```python
import numpy as np
import matplotlib.pyplot as plt

x = np.arange(1920)
y = np.arange(1080)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2) / 50)

plt.imshow(Z, cmap='gray')
plt.title('Circular Pattern')
plt.show()
```

The **`np.eye`** function in NumPy creates an identity matrix. An identity matrix is a square matrix where all the elements of the main diagonal are 1, and all other elements are 0.

### *np.eye(N, M=None, k=0, dtype=float, order='C')*

The syntax is **`np.eye(N, M=None, k=0, dtype=float, order='C')`**, where **`N`** is the number of rows in the matrix. **`M`**, optional, is the number of columns in the matrix and, if not specified, assumes the same value as **`N`**, thus creating a square matrix. The **`k`** parameter, also optional, specifies the diagonal index: the main diagonal is **`k=0`**, diagonals above the main diagonal have **`k>0`**, and those below the main diagonal have **`k<0`**. **`dtype`** indicates the data type of the matrix elements, which by default is **`float`**. **`Order`** specifies the memory order of the elements ('C' for C-style, 'F' for Fortran-style).

```python
I = np.eye(3)
[[1. 0. 0.] 
 [0. 1. 0.] 
 [0. 0. 1.]]
```

By increasing or decreasing the value of **`k`**, you can change the position of the diagonal:

```python
I_shift = np.eye(3, 3, k=1)
[[0. 1. 0.]
 [0. 0. 1.]
 [0. 0. 0.]]
```
Here is the translation of the text:

---

## **2.5.2 - NUMPY SLICE**

NumPy has a system for manipulating arrays similar to what we use in Python, such as in lists, called slicing.

```python
array[start:stop:step]
```

Slices allow you to access and modify subsets of arrays without creating unnecessary copies of the data, making the code faster and more readable.

If **`start`** is omitted, the array starts from the first element; **`stop`** indicates the last element, while **`step`** indicates the step between each element (default is 1). **`[: : 2]`** means from the first to the last, every two.

For example:

```python
# Create an 8x8 white matrix  
whiteMat = np.ones((8, 8), dtype=np.uint8) * 255

# Create an 8x8 black matrix  
blackMat = np.zeros((8, 8), dtype=np.uint8)

# Create an empty 8x8 image (to hold half of one and half of the other)  
combinedMat = np.zeros((8, 8), dtype=np.uint8)

# Combine the two matrices  
combinedMat[:, :4] = whiteMat[:, :4]  
combinedMat[:, 4:] = blackMat[:, 4:]

# Display the combined image  
plt.imshow(combinedMat, cmap='gray')  
plt.title('Half White and Half Black')

plt.show()
```

The operation **`[:, :4]`** selects all rows and the first 4 columns of the array.

When talking about slicing, it might be helpful to remember that the first element is 0 and the second is 1. Sometimes this can be confusing, especially when working with matrices. For example, **`array[0, 0]`** accesses the element in the first row and first column, while **`array[1, 2]`** accesses the element in the second row and third column.

Another way to use slicing is to insert a comma instead of the stop. In this case, you specify a two-dimensional slice **`[rowStart:rowStop, colStart:colStop]`**. It is a bit counterintuitive because, in this case, you indicate the number of rows and columns instead of the position. For example, **`array[:, 4:]`** selects all rows and columns from the fourth onward.

These two methods may seem similar in writing, but it is important not to confuse them: one is used to access specific elements, while the other is used to select ranges of rows and columns.

Later, we will see how this allows us to perform a wipe fade between two images. For now, let's limit ourselves to creating an E.B.U. ([European Broadcast Union](https://www.ebu.ch/home)) color bars generator.

```python
from matplotlib import pyplot as plt  
import numpy as np

colors = [  
   (192, 192, 192),  # Gray  
   (192, 192, 0),    # Yellow  
   (0, 192, 192),    # Cyan  
   (0, 192, 0),      # Green  
   (192, 0, 192),    # Magenta  
   (192, 0, 0),      # Red  
   (0, 0, 192),      # Blue  
   (0, 0, 0)         # Black  
]

width, height = 1920, 1080  
# Create an empty matrix  
bar_height = height  
bar_width = width // len(colors)  
bars = np.zeros((bar_height, width, 3), dtype=np.uint8)

# Fill each section with the corresponding color  
for i, color in enumerate(colors):  
   bars[:, i * bar_width:(i + 1) * bar_width, :] = color

plt.imshow(bars)  
plt.title('Colored Bars')

plt.show()
```

**`np.arange`** is a NumPy function that generates an array containing equally spaced values within a specified range. It is similar to Python's **`range`** function but returns a NumPy array instead of a range object.

### *numpy.arange(\[start, \]stop, \[step, \]dtype=None, \*, device=None, like=None)*

Where *start (optional)* is the beginning of the interval and defaults to 0, *stop* is the end of the interval - *The interval does not include this value* - *step* (optional) is the spacing between values (default is 1), and *dtype* (optional) is the data type of the resulting array. If not specified, the data type is inferred from the other arguments.

*Device* (optional) is the device on which to place the created array. Default: None, while *like* (optional) is a reference object to allow the creation of arrays that are not NumPy arrays.

```python
import numpy as np  
import matplotlib.pyplot as plt  
arr = np.arange(0, 1920, dtype=np.uint8)  
arr = np.tile(arr, (1080, 1))  
print(arr)  
print(arr.shape)  
print(arr.dtype)  
print(arr.min(), arr.max())

plt.imshow(arr, cmap='gray')  
plt.show()
```

In this example, you would expect to see a gradient. However, since **`uint8`** ranges from 0 to 255, the values "wrap around" to 0, causing repetitions instead of a continuous gradient. This can still be useful for creating regular patterns.

Here is an example of creating an 8x8 grid with vertical bars using **`np.arange`**:

```python
import numpy as np  
import matplotlib.pyplot as plt

# Create an 8x8 grid with vertical bars  
bar_height = 8  
bar_width = 8

# Create an array of column indices  
columns = np.arange(bar_width)

# Alternate between white (255) and black (0) columns  
bars = (columns % 2) * 255

# Repeat the vertical bars across all rows  
bars = np.tile(bars, (bar_height, 1))

plt.imshow(bars, cmap='gray')  
plt.title('Vertical Bars')  
plt.show()
```

**`np.mgrid`** is a very useful tool for creating multidimensional mesh grids, which are essentially coordinates in a multidimensional space. This can be particularly useful for graphics, visualization, and creating regular patterns or grids of points. Here is an example to create a circular pattern:

```python
import numpy as np  
import matplotlib.pyplot as plt

x = np.arange(1920)  
y = np.arange(1080)  
X, Y = np.meshgrid(x, y)  
Z = np.sin(np.sqrt(X**2 + Y**2) / 50)

plt.imshow(Z, cmap='gray')  
plt.title('Circular Pattern')  
plt.show()
```

The **`np.eye`** function in NumPy creates an identity matrix. An identity matrix is a square matrix where all the elements of the main diagonal are 1, and all other elements are 0.

### *np.eye(N, M=None, k=0, dtype=float, order='C')*

The syntax is **`np.eye(N, M=None, k=0, dtype=float, order='C')`**, where **`N`** is the number of rows in the matrix. **`M`**, optional, is the number of columns in the matrix and, if not specified, assumes the same value as **`N`**, thus creating a square matrix. The **`k`** parameter, also optional, specifies the diagonal index: the main diagonal is **`k=0`**, diagonals above the main diagonal have **`k>0`**, and those below the main diagonal have **`k<0`**. **`dtype`** indicates the data type of the matrix elements, which by default is **`float`**. **`Order`** specifies the memory order of the elements ('C' for C-style, 'F' for Fortran-style).

```python
I = np.eye(3)
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]
```

By increasing or decreasing the value of **`k`**, you can change the position of the diagonal:

```python
I_shift = np.eye(3, 3, k=1)
[[0. 1. 0.]
 [0. 0. 1.]
 [0. 0. 0.]]
```

## **2.5.3 - NUMPY STACK**

In addition to the manipulation methods we have seen, such as slicing to insert values or creating vectors to stack, NumPy also offers functionalities to combine and divide matrices efficiently.

NumPy's stacking functions allow you to combine multiple matrices together. For example, **`vstack`** combines matrices vertically, while **`hstack`** combines them horizontally. You can achieve similar results with **`concatenate`** by specifying the axis: 0 for combining along the row axis (vertical) and 1 for combining along the column axis (horizontal).

```python
import numpy as np

A = np.ones((2, 2))  
B = np.zeros((2, 2))

# Stack vertically  
vstack_result = np.vstack((A, B))  
print("Vertical Stack Result:")  
print(vstack_result)

# Stack horizontally  
hstack_result = np.hstack((A, B))  
print("Horizontal Stack Result:")  
print(hstack_result)

Vertical Stack Result:
[[1. 1.]
[1. 1.]
[0. 0.]
[0. 0.]]
Horizontal Stack Result:
[[1. 1. 0. 0.]
[1. 1. 0. 0.]]
```

The **`block`** function in NumPy is used to combine arrays into a larger matrix according to a specified layout. You can think of this function as a way to combine smaller arrays into a single larger array, organizing them into a grid.

```python
import numpy as np

A = np.ones((2, 2))  
B = np.eye(2, 2)  
C = np.zeros((2, 2))  
D = np.diag((-3, -4))

result = np.block([[A, B], [C, D]])

# A = [[1, 1],     B = [[1, 0],    C = [[0, 0],    D = [[-3, 0],
#      [1, 1]]          [0, 1]]         [0, 0]]         [ 0, -4]]

print(result)

[[ 1.,  1.,  1.,  0.],
[ 1.,  1.,  0.,  1.],
[ 0.,  0., -3.,  0.],
[ 0.,  0.,  0., -4.]]
```

In addition to combining matrices, NumPy also offers several ways to split arrays into sub-arrays. These methods are useful for partitioning data. The **`split`** function divides an array into multiple sub-arrays as views of the original array.

```python
import numpy as np

A = np.arange(16).reshape(4, 4)  
# Divide A into two sub-arrays along axis 1 (horizontal)  
split_result = np.split(A, 2, axis=1)  
print("Split Result:")  
print(split_result)


Split Result: 
[array(\[\[ 0, 1\], \[ 4, 5\], \[ 8, 9\], \[12, 13\]\]),

array(\[\[ 2, 3\], \[ 6, 7\], \[10, 11\], \[14, 15\]\])\]

```

Sometimes you may need to unpack the three RGB channels of an image or perform the reverse operation. The **`dstack`** function in NumPy is used to stack arrays along the third axis (depth), while **`dsplit`** splits an array along the third axis. So, **`dsplit`** can be considered the inverse operation of **`dstack`**.

```python
import numpy as np

# Create three 2x2 matrices for the R, G, and B channels  
R = np.array([[255, 0], [0, 255]])  
G = np.array([[0, 255], [255, 0]])  
B = np.array([[0, 0], [255, 255]])

# Stack the three matrices along the third axis to create an RGB image  
RGB = np.dstack((R, G, B))  
print("Image RGB:")  
print(RGB)

# Split the RGB image along the third axis to obtain the R, G, and B channels  
R_split, G_split, B_split = np.dsplit(RGB, 3)  
print("\nChannel R:")  
print(R_split)  
print("\nChannel G:")  
print(G_split)  
print("\nChannel B:")  
print(B_split)
```

The **`vsplit`** and **`hsplit`** functions split an array into multiple sub-arrays along the vertical axis (rows) and horizontal axis (columns), respectively. This means you can split an image into equal parts either horizontally or vertically.

```python
import numpy as np  
import matplotlib.pyplot as plt

# Create a matrix representing an RGB image (e.g., 4x4 pixels with 3 channels)  
image = np.array([  
   [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],  
   [[255, 0, 0], [255, 0, 0], [0, 255, 0], [0, 255, 0]],  
   [[0, 0, 255], [0, 0, 255], [255, 255, 0], [255, 255, 0]],  
   [[0, 0, 255], [0, 0, 255], [255, 255, 0], [255, 255, 0]]  
], dtype=np.uint8)

# Split the image into two equal parts along the vertical axis  
top_half, bottom_half = np.vsplit(image, 2)

# Display the split images  
plt.subplot(1, 2, 1)  
plt.imshow(top_half)  
plt.title('Top Half')

plt.subplot(1, 2, 2)  
plt.imshow(bottom_half)  
plt.title('Bottom Half')

plt.show()
```

These NumPy functions allow you to efficiently manipulate and visualize images, facilitating the creation of patterns and the partitioning of data for further analysis.


Here is the translation of the text:

---

## **2.6 - EXECUTION TIME**

After understanding how to create and manipulate matrices in NumPy, it becomes easy to grasp how to perform arithmetic operations on them. NumPy allows for operations like multiplication, addition, division, and subtraction in a very intuitive and fast manner.

As we can infer, performing an operation on an image using NumPy is relatively simple. An image is a cubic matrix, but despite this fancy name, multiplying or adding a constant value is a breeze. You just need to write **`x * 1.2`** or **`x + 0.01`**, where **`x`** is our matrix.

When working with video, one of the main challenges is maintaining the correct frame rate. For standard video, this means performing all necessary operations within 1/60 of a second to maintain a frame rate of 60 fps. This time constraint requires that every blending calculation or contrast operation be extremely efficient because every extra millisecond could make a difference. Additionally, working with the **`uint8`** system can sometimes be misleading.

## **2.6.1 - Considerations on Operations in `uint8`**

The **`uint8`** format (8-bit unsigned integer) represents pixel values as integers between 0 and 255. This can create some pitfalls. The most common problem arises when multiplying two **`uint8`** matrices together. In the formulas we've seen, white is normalized to 1. This means that any color multiplied by 1 remains the same, while any color multiplied by 0 becomes black. But if white is 255, we don't get the same result.

As long as I multiply my image by a constant value, there are no issues, but to understand which operations we can use, we need to introduce time.

## **2.6.2 - Measuring Execution Time**

To maintain a 60fps frame rate, we must perform all operations within 1/60 of a second. To do this, we can use PyQt6, which provides a timer and allows emitting a signal that can be used in other classes by connecting a function.

Here’s an example of how to create an object to establish the time:

```python
class SynchObject(QObject):  
   synch_SIGNAL = pyqtSignal()

   def __init__(self, fps=60, parent=None):  # Set FPS to 60  
       super().__init__(parent)  
       self.fps = fps  
       self.syncTimer = QTimer(self)  
       self.syncTimer.timeout.connect(self.sync)  
       self.syncTimer.start(1000 // fps)  
       self._initialized = True

   def sync(self):  
       self.synch_SIGNAL.emit()
```

The Synch class is very simple; it's essentially a clock that is created once and emits a signal every 1/60 of a second.

The **`SynchObject`** class is very simple; it's basically a clock that emits a signal every 1/60 of a second. In PyQt, there is this signal method that allows data to be sent from one part of the code to another. If the data type (str, int, float) is not specified, by default it is a boolean true value.

I created this quick example to clarify the signals. Class1 has a button; I can connect the click to the emission of a signal that can be intercepted by Class2 to make something happen.

```python
from PyQt6.QtCore import QObject, pyqtSignal  
from PyQt6.QtWidgets import QPushButton, QLabel

class class1(QObject):  
   segnaleEseguito = pyqtSignal()

   def __init__(self):  
       super().__init__()

       self.button = QPushButton("Click Me")  
       self.button.clicked.connect(self.funzione_da_eseguire)  
       self.button.show()

   def funzione_da_eseguire(self):  
       print("The button has been clicked!")  
       self.segnaleEseguito.emit()

class class2(QObject):

   def __init__(self):  
       super().__init__()  
       self.class1 = class1()  
       self.class1.segnaleEseguito.connect(self.funzione_da_eseguire)  
       self.lbl = QLabel("Waiting for the signal")  
       self.lbl.show()

   def funzione_da_eseguire(self):  
       self.lbl.setText("The signal has been emitted")

if __name__ == '__main__':  
   import sys  
   from PyQt6.QtWidgets import QApplication

   app = QApplication(sys.argv)  
   window1 = class1()  
   window2 = class2()  
   sys.exit(app.exec())
```

## **2.6.3 - Synchronizing Output and Input**

Using the signal system, we can create synchronization between input and output. However, it is crucial that every operation occurs within the signal clock time; otherwise, the previous image will be used. This can cause the perception of a slowdown in the video.

When working with real-time video, each frame must be processed within a certain time interval to maintain a constant frame rate. In our case, with a frame rate of 60 fps, each operation must be completed within 1/60 of a second. If the operation is not completed in time, the system will use the previous frame, causing a noticeable delay in the video output.

```python
import numpy as np  
from PyQt6.QtCore import QObject

class randomNoiseGenerator(QObject):

   def __init__(self, synch, parent=None):  
       super().__init__(parent)  
       self._frame = np.zeros((1080, 1920, 3), dtype=np.uint8)  
       self.synch = synch  
       self.synch.synch_SIGNAL.connect(self.captureFrame)

   def captureFrame(self):  
       self._frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)  
        
   def getFrame(self):  
       return self._frame
```

To display the animated image, we can use a QLabel, using the same synch object to update the image display:

```python
import numpy as np  
from PyQt6.QtCore import *  
from PyQt6.QtGui import *  
from PyQt6.QtWidgets import *

class TestNumpy(QObject):

   def __init__(self, synch, parent=None):  
       super().__init__(parent)  
       self._frame = np.zeros((1080, 1920, 3), dtype=np.uint8)  
       self.synch = synch  
       self.synch.synch_SIGNAL.connect(self.captureFrame)

   def captureFrame(self):  
       self._frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

   def getFrame(self):  
       return self._frame

class VideoApp(QWidget):

   def __init__(self, synch, test, parent=None):  
       super().__init__(parent)  
       self.lblViewer = QLabel()  
       self.synch = synch  
       self.test = test  
       self.synch.synch_SIGNAL.connect(self.updateViewer)

       self.layout = QVBoxLayout()  
       self.layout.addWidget(self.lblViewer)  
       self.setLayout(self.layout)  # Apply the layout to the window

   def updateViewer(self):  
       frame = self.test.getFrame()  
       qImage = QImage(frame.data, frame.shape[1], frame.shape[0],  
                                        QImage.Format.Format_RGB888)  
       self.lblViewer.setPixmap(QPixmap.fromImage(qImage))

if __name__ == "__main__":  
   import sys  
   from cap2.cap2_5.synchObject import SynchObject

   app = QApplication(sys.argv)  
   synch = SynchObject(60)  
   test = TestNumpy(synch)  
   video = VideoApp(synch, test)  
   video.show()  
   sys.exit(app.exec())
```

Here's the continuation of the translation starting from section 2.6.4:

---

## **2.6.4 - Impact on Frame Rate**

If the required operations on the frame are not completed within the clock time (1/60 of a second), the system will use the previous frame. This delay can cause a perception of video slowdown, as the frames are not updated in real-time.

To avoid this problem, it's important to optimize the operations we perform on the frames. For example, complex operations such as logarithmic transformation or contrast adjustment with non-linear functions can take more time compared to simple addition or multiplication operations.

## **2.7 - MEASURING TIME**

Synchronization between input and output is crucial for maintaining a constant frame rate and ensuring a smooth video experience. Using the signal system in PyQt6, we can ensure that each operation occurs within the clock time, minimizing the risk of video slowdowns. Optimizing matrix operations is essential to meet these time constraints and maintain high video quality.

Optimizing the mathematics in matrix operations is not simple. There is a course at MIT on this topic, 6.172 - Performance Engineering of Software Systems, taught by Professors Charles Leiserson and Julian Shun, which delves into this subject and is also available on YouTube.

There are at least two other aspects to consider besides the algorithm itself: the operating system and Python. It might seem trivial, but without data, it's hard to understand how to change the code to make it faster.

A simple way to measure execution time in Python is to use the **`time`** library:

```python
import time

def payload():  
   pass

start = time.time()  
payload()  # execute a load  
print(f"Execution time: {time.time() - start:.6f} seconds")
```

The **`time.time()`** function returns the number of seconds elapsed since midnight on January 1, 1970, until the moment it is called. By saving the initial value in a variable, we can subtract the value at the end of the operation and print the time taken.

However, measuring the execution time only once may not be indicative. It's better to measure an average time by repeating the operation multiple times.

For this reason, many use **`timeit (pip install timeit)`**, which provides a more reliable and scientific result.

```python
from timeit import timeit

def payload():  
   pass

timeIT = timeit(payload, number=10)  
print(f"Average execution time for 10 runs: {timeIT:.6f} seconds")
```

Another very useful tool is **`cProfile`**, which is used to measure the execution time of different parts of the code. This process is called **deterministic profiling**. Python, as it is written, monitors all events of function calls, returns, and exceptions, measuring the precise times between these events and providing detailed statistics on the program's execution. Using **`cProfile`** requires some resources, but it allows us to easily identify unwanted bottlenecks because it provides a detailed report of function calls. Here’s a practical example:

```python
import cProfile

def slow_function():  
   total = 0  
   for i in range(10000):  
       total += sum(j for j in range(100))  
   return total

def main():  
   result = slow_function()  
   print(result)

if __name__ == "__main__":  
   cProfile.run('main()')


*49500000*
*1020006 function calls in 0.112 seconds*
   *Ordered by: standard name*
   *ncalls  tottime  percall  cumtime  percall filename:lineno(function)*

    	*1	0.000	0.000	0.112	0.112 <string>:1(<module>)*
    	*1	0.003	0.003	0.112	0.112 profileTest.py:3(slow_function)*
                   *1010000	0.050	0.000	0.050	0.000 profileTest.py:6(<genexpr>)*
    	*1	0.000	0.000	0.112	0.112 profileTest.py:9(main)*
    	*1	0.000	0.000	0.112	0.112 {built-in method builtins.exec}*
    	*1	0.000	0.000	0.000	0.000 {built-in method builtins.print}*
	*10000	0.060	0.000	0.109	0.000 {built-in method builtins.sum}*
    	*1	0.000	0.000	0.000	0.000 {method 'disable' of '_lsprof.Profiler' objects}*
```

The report tells us that the program made a total of 1,020,006 function calls and took 0.112 seconds to execute. Most of the time (0.060 seconds) is spent in the **`sum`** function, called 10,000 times, and there is a **`<genexpr>`** function, which takes 0.050 seconds and is called 1,010,000 times, indicating a repetitive and costly operation.

This is one of the cases where large language models like GPT, Gemini, and Claude can help you understand these reports. In our case, **`genexpr`** is the generator expression **`j for j in range(100)`**, which is causing the slowdown. Our way of writing the code can cause unexpected slowdowns, and we only notice them when we put everything together. Thanks to this check, we can optimize the **`slow_function`**:

```python
import cProfile

def slow_function_optimized():  
   total = 0  
   for i in range(10000):  
       total += sum(range(100))  
   return total

def main_optimized():  
   result = slow_function_optimized()  
   print(result)

cProfile.run('main_optimized()')


 *49500000*
*10006 function calls in 0.005 seconds*
   *Ordered by: standard name*

   *ncalls  tottime  percall  cumtime  percall filename:lineno(function)*

    	*1	0.000	0.000	0.005	0.005 <string>:1(<module>)*
    	*1	0.001	0.001	0.005	0.005 profileTest.py:18(slow_function_optimized)*
    	*1	0.000	0.000	0.005	0.005 profileTest.py:24(main_optimized)*
    	*1	0.000	0.000	0.005	0.005 {built-in method builtins.exec}*
    	*1	0.000	0.000	0.000	0.000 {built-in method builtins.print}*
	*10000	0.003	0.000	0.003	0.000 {built-in method builtins.sum}*
    	*1	0.000	0.000	0.000	0.000 {method 'disable' of '_lsprof.Profiler' objects}*
```
We see a difference from 0.112 to 0.005 seconds while obtaining the same result.

That said, we can then move on to the other two aspects that are part of the optimization rhetoric.

The first aspect concerns the operating system. Even if we optimize an operation to save 0.01 seconds, the operating system may have hundreds or thousands of threads open for other operations because marketing needs to know who you are to create a personalized desire for you. All this could interfere with our optimization.

The second aspect is Python itself. Python is an interpreted language, which adds an external level of complexity to the code we've written. Each instruction must be interpreted and translated into machine code in real-time, which introduces overhead compared to compiled languages like C++. For this reason, measuring execution time is the first thing to do.

Here is the translation for the remaining part starting from section 2.7.1:

---

## **2.7.1 - Complexity: Big "O"**

In computer science, the efficiency of algorithms is measured in "Big O", which describes how the execution time or space used by an algorithm grows as the input size increases. Here are some of the most common Big O notations:

* **O(1):** Constant time. The algorithm takes the same amount of time regardless of the input size.
* **O(log n):** Logarithmic time. The algorithm takes less time for each increase in input.
* **O(n):** Linear time. The execution time grows linearly with the input size.
* **O(n log n):** Log-linear time. Often used in efficient sorting algorithms.
* **O(n^2):** Quadratic time. The execution time grows proportionally to the square of the input size.

For example, we get a complexity of O(n^2) whenever we nest two for loops together. If, for instance, Python or another language adds its own loops to interpret the code, the complexity increases. Therefore, finding the best way to write the algorithm is crucial.

I place it second because efficiency is determined for n numbers and in the worst-case scenario. Sometimes, there may be a range of values where the worst case will never happen, and with the same "O", a function with O(n^2) may be faster than one with O(log n)!

```python
from timeit import timeit

def op1():  
   for x in range(1, 1920):  
       for y in range(1, 1080):  
           pass  # Do something here, for example: z = x * y

# Measure the execution time of the `op1` function with 10 executions  
execution_time = timeit(op1, number=10)  
print(f"Execution time for 10 runs of op1: {execution_time:.6f} seconds")
```

### *Execution time for 10 runs of op1: 0.192328 seconds*

This means that each op1 uses 0.019 seconds, too long for a smooth animation that requires less than 0.016 seconds per frame (60 fps).

## **2.7.2 - Overhead**

When writing code in Python, we must consider that every operation introduces some overhead. For example, a matrix multiplication operation with O(n^2) complexity will be slower in Python compared to a compiled language due to the additional time needed for code interpretation.

Overhead is an important concept to understand. In Python, when we create a variable, the language has to handle several background tasks, such as memory allocation and type inference. This process requires additional time and resources compared to compiled or low-level languages.

Python uses a more complex memory management system compared to simple register allocation. Objects in Python have additional overhead to store information like the data type and reference count.

←-------------- space used \------\> ←----- overhead----\>

|0||0||0||0||0||0||0||0||0||0||0||0||0||0||0||0||0||0||0||0|....64

This incurs time costs because, for example, if I consider my number 0-255 at 8 bits, in a single 64-bit register, I can fit 8 pixels!

NumPy is implemented in C, and when we create a data structure like a matrix in NumPy, it might, for example, pack 8 pixels into a single register, making the matrix 8 times smaller.

```python
import numpy as np

def op2():  
   w = 1920  
   h = 1080  
   x = np.arange(1, w)  
   y = np.arange(1, h)  
   return np.sum(np.outer(x, y))

execution_time = timeit(op2, number=10)  
print(f"Execution time for 10 runs of op2: {execution_time:.6f} seconds")
```

### 

### *Execution time for 10 runs of op2: 0.040971 seconds!*

The other good news is that OpenCV uses NumPy to represent images, and both can perform operations very, very fast, and by the end of this chapter, we'll understand how.

## **2.7.3 - Numpy LightSpeed**

Optimizing code is not just a matter of reducing the number of operations but also choosing the right operations for the hardware and the language used. For example, NumPy matrix operations are optimized to perform parallel calculations using high-performance libraries written in C.

Choosing the right way to write the code, such as using NumPy's vectorized functions instead of Python loops, can make a significant difference in performance. Measuring execution time and profiling the code allows us to understand where the bottlenecks are and optimize the slowest parts to improve the video frame rate.

Vectorization in NumPy is a fundamental concept that allows operations on entire arrays to be performed efficiently without explicit loops. This means that to traverse a matrix and perform any kind of operation, the classic method is to nest two for loops:

```python
from timeit import timeit  
import numpy as np

# Create random matrices  
A = np.random.rand(1920, 1080)  
B = np.random.rand(1920, 1080)

# Function for traditional multiplication with for loop  
def traditional_multiplication(A, B):  
   result = np.zeros(A.shape)  
   for i in range(A.shape[0]):  
       for j in range(A.shape[1]):  
           result[i, j] = A[i, j] * B[i, j]  
   return result

# Measure execution time for vectorized multiplication  
execution_time_vectorized = timeit(lambda: A * B, number=10)  
print(f"Execution time for 10 runs of vectorized multiplication: {execution_time_vectorized:.6f} seconds")

# Measure execution time for traditional multiplication  
execution_time_traditional = timeit(lambda: traditional_multiplication(A, B), number=10)  
print(f"Execution time for 10 runs of traditional multiplication: {execution_time_traditional:.6f} seconds")
```

Any mathematical operation between matrices in NumPy is vectorized, meaning the operation is the process of converting scalar operations (which operate on single elements) into vector operations (which operate on entire arrays).

These are special instructions called SIMD (Single Instruction, Multiple Data) provided by C compilers to optimize certain calculations. This essentially means that NumPy handles matrices not by using a nested for loop but by considering the matrix as a single entity.
```
*Execution time for 10 runs of vectorized multiplication: 0.038088 seconds*
*Execution time for 10 runs of traditional multiplication: 3.906912 seconds*
```
This includes arithmetic operations like +, -, *, /, *, some mathematical functions: np.sin(), np.exp(), np.log(), logical operations >, <, ==, !, and reduction functions: np.sum(), np.mean(), np.max().



