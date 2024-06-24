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
- Compatibility: Tested on Windows 10 and Windows 11. While theoretically portable to Linux, the screen capture component, based on Ra1nty Rain's DXCam (capable of 240Hz+ capturing! - "https://github.com/ra1nty/DXcam"), would need to be rewritten for Linux.

![OpenPyVision](https://github.com/AlessioMichelassi/openPyVision_013/blob/master/imgs/version012.png)

Experience the power and flexibility of OpenPyVision for your real-time video mixing needs.

audio coming next

# Installation
1. Download the latest release from the [Releases](
2. Extract the contents of the zip file to a folder.
3. Run the executable file.
4. Enjoy!

openPyVision use FFmpeg in some cases, so you need to have it installed on your system. You can download it from the official website.


# Installation

1. **Download FFMPEG**:
   - Visit [FFmpeg official download page](https://ffmpeg.org/download.html).
   - Download the appropriate version for your operating system.

2. **Unzip**:
   - Unzip the downloaded file to a desired folder.

3. **Add to System Environment Variables**:
   - Add the path to the `ffmpeg/bin` directory to your system environment variables:
     - Open Command Prompt as Administrator.
     - Run the following command:
       ```sh
       setx path "%path%;C:\path\to\ffmpeg\bin" /M
       ```
     - Replace `C:\path\to\ffmpeg\bin` with the actual path where you unzipped FFmpeg.

4. **Verify Installation**:
   - Open a new Command Prompt window.
   - Type the following command to check if FFmpeg is installed correctly:
     ```sh
     ffmpeg -version
     ```
   - You should see the version information of FFmpeg.

```sh
ffmpeg -version
```

### Example Output
```
ffmpeg version 4.4.1 Copyright (c) 2000-2021 the FFmpeg developers
built with gcc 10.3.0 (GCC)
configuration: --enable-gpl --enable-version3 .... etc
```

### Note
If you encounter any issues, please refer to the [FFmpeg documentation](https://ffmpeg.org/documentation.html) for further assistance.
