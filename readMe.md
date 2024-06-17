# OpenPyVision (oPV)

OpenPyVision (oPV) is a real-time video mixer that allows you to mix videos with effects and transitions seamlessly.
Key Features:

- Input Sources: Choose from a variety of input sources in the input matrix section, including screen capture, video capture, and images.
- Default Setup: By default, the program opens with two HD 1920x1080 screens – one for output and one for the interface to control the program.
- Interface Design: The interface is designed to resemble a vision mixer rather than a graphic mixer, offering advantages in space and quick access to functions. In addition to cut and mix, you can load animated stings for transitions and insert keys for subtitles, tickers, or bugs.
- Input Modification: Modify each input by adjusting gamma, inverting the image, applying an unsharp mask filter, or increasing brightness.
- Virtual Inputs: Create two-box effects like 50:50, 70:30, or 30:70, allowing for multiple picture-in-picture setups. Easily switch inputs on the fly for scenarios like a presenter narrating with accompanying images or videos, or in talk shows where inputs frequently change.
- Preview and Program Monitors: Once inputs are selected from the matrix, you can place them in preview or program (live). Use the preview and program monitors for operations like zoom and pan, adjusting R, G, B channels, and viewing histograms. The main out supports navigation and zoom with the middle mouse button, fit view with the right button, and pointing with the left button (helpful for on-screen indications).
- Effects and Transitions: Utilize various effects for mixing, such as fade, wipe, push, and slide. Apply transition effects like crossfade, dip to image/color, and stings. The still button lets you display a fixed image, useful for airing signs or placeholders.
- MixBus and CleanFeed: Use the mix bus to create a clean feed, which can then be enhanced with images or sequences with alpha channels to produce the dirty feed for the main output.

Technical Details:

- Development: The program is written in Python 3.10, utilizing PyQt5 for the graphical interface and OpenCV for video manipulation. The current version is being updated to PyQt6.
- Open Source: OpenPyVision is open source with no commercial limitations. If you find something useful, please credit the author or the program.
- Compatibility: Tested on Windows 10 and Windows 11. While theoretically portable to Linux, the screen capture component, based on Ra1nty Rain's DXCam (capable of 240Hz+ capturing!), would need to be rewritten for Linux.

Experience the power and flexibility of OpenPyVision for your real-time video mixing needs.