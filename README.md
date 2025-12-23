<a id="readme-top"></a>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Aion 2 DPS Meter</h3>
  <p align="center">
    Real-time DPS meter for Aion 2 using OCR-based combat log analysis
  </p>
</div>


<!-- ABOUT THE PROJECT -->
## About The Project

A real-time DPS (Damage Per Second) meter specifically designed for **Aion 2**. The application captures screenshots of the in-game combat log, uses OCR (Optical Character Recognition) to extract text, and calculates damage metrics with live visualization.

If u need Chinese version, use @crazzyHuang solution available here:  https://github.com/crazzyHuang/aion2_dps_meter

### Key Features

* **Real-time DPS Visualization** - Live graphs showing moving average and overall average DPS
* **Multi-threaded Architecture** - Efficient screen capture and OCR processing using thread pools
* **Intelligent Log Parsing** - Detects damage events, skill names, targets, and critical hits
* **Optimized Screen Capture** - Only processes new combat log entries, ignoring duplicate frames
* **Configurable** - Easy setup through `config.ini` file
* **Debug Mode** - Optional OCR visualization and detailed logging

### How It Works

1. **Screen Capture** - Continuously captures a specified region of the screen where the combat log is displayed
2. **Image Preprocessing** - Extracts colored text (damage, skills, names) and upscales for better OCR accuracy
3. **OCR Processing** - Uses Tesseract to recognize text from processed images in parallel threads
4. **Log Parsing** - Detects new combat log entries and extracts damage information using regex patterns
5. **DPS Calculation** - Computes moving average (1-second window) and overall average damage
6. **Real-time Plotting** - Displays interactive graphs using matplotlib with live updates

<!-- REQUIREMENTS -->
## Requirements

Aion 2 with Large UI scale and Aion 1 control mode.

* **Python 3.12** (tested and verified)
* **Tesseract OCR** (external dependency)
* **Windows OS** (for screen capture functionality)

<!-- INSTALLATION -->
## Installation

### 1. Install Tesseract OCR

Download and install Tesseract OCR from the official repository:

**Windows:**
- Download installer: https://github.com/UB-Mannheim/tesseract/wiki
- Run the installer and note the installation path (default: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

**Note:** The path to Tesseract must be configured in `config.ini` after installation.

### 2. Clone/Download the Repository


### 3. Install Python Dependencies
Make sure you have Python 3.12(tested on it) installed and added to your PATH.
From the project root directory, install all required Python packages:
```
pip install -r requirements.txt
```
If you have multiple Python versions installed, you may need to use:
```
python -m pip install -r requirements.txt
```

### 4. Configure the Application
Before running the app, open config.ini and configure:
Tesseract path (e.g. C:\Program Files\Tesseract-OCR\tesseract.exe)
Screen capture region according to your monitor resolution
Combat log position (must be full-height combat chat)

Important notes:
- Combat chat must be set to Combat and opened in full height
- UI Proportion must be set to Larger(tested with it)
- Use Aion 1 control mode to prevent the combat log window from closing

### 5. Run the Application
Start the DPS meter by running:
```
python main.py
```
Once running:
The app will begin capturing the combat log region
DPS data will be calculated in real time
A live matplotlib window will display DPS graphs
If ocr_view is enabled, an OCR debug window will appear

<!-- Notes -->
## Notes

App was created for myself and cleaned up before release to github.

I tested it with 2 monitors with requirements mentioned upper. Feel free to fork. Code can have bugs or bad patterns.

Use with Large UI scale and Aion 1 control mode(prevents combat log window close).

Data gathered from combat log can be used in more detailed analysis(by skills/by multiplier types)

<!-- Screenshots -->
## Screenshots

This is how should the combat chat look like to capture:

![screenshot-1]

I recommend to set region like this:

![screenshot-2]

Example DPS meter plot showing damage:

![screenshot-3]

If ocr_view enabled u can debug it viewing next window. Keep in mind that it works ugly now and window will be movable only on incoming combat log updates.

![screenshot-4]

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[Python]: https://img.shields.io/badge/python-3783ed?style=for-the-badge&logo=python&logoColor=ffffff
[Python-url]: https://www.python.org/

[screenshot-1]: images/combat_log.png
[screenshot-2]: images/capture_region.png
[screenshot-3]: images/plot.png
[screenshot-4]: images/ocr_debug.png
