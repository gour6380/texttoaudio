
# Text to Audio Conversion Service

This project is a web-based service designed to convert text to audio using a custom Python script integrated with a Vapor web server. It allows users to upload conversation data and speaker preferences, which are then processed to generate audio files.

## Features

- Convert text to audio using custom-defined speaker data.
- List and download generated audio files.
- Support for `.mp3` and `.wav` audio formats.
- Integration with external Text-to-Speech API for audio generation.

## Requirements

- Swift 5.2 or later
- Vapor 4
- Python 3.7 or later
- PythonKit
- External libraries: `pydub`, `requests`

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/gour6380/texttoaudio.git
   cd texttoaudio
   ```

2. **Install Swift dependencies**

   Navigate to your Swift project directory and use Vapor's dependency manager to install the required Swift packages.

   ```bash
   vapor update
   ```

3. **Install Python dependencies**

   It's recommended to create a virtual environment for Python to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

   `requirements.txt` should include `pydub` and `requests`.

4. **Environment Variables**

   Set the necessary environment variables such as `LOVA_DELFY_KEY` for the external Text-to-Speech API access.

   ```bash
   export LOVA_DELFY_KEY='your_api_key_here'
   ```

## Usage

1. **Start the Vapor server**

   Run the Vapor project to start the server.

   ```bash
   vapor run
   ```

2. **Accessing the Web Interface**

   Open a web browser and navigate to `http://localhost:8080/` to access the web interface for uploading conversation data and speaker preferences.

3. **API Endpoints**

   - `POST /convert`: Convert text to audio using the uploaded JSON data.
   - `GET /list`: List the available audio files for download.

4. **Running Python Script Independently**

   The Python script can be run independently for testing purposes.

   ```bash
   python main.py
   ```
