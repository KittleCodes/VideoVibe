# VideoVibe

VideoVibe is a video streaming platform that allows users to upload, share, and watch videos.

## Features

- Upload videos
- Videos are automatically transcribed
- Comment system
- User and channel system

## Todo
- Redesign video upload page
- Add studio to control channels and their content

## Technologies Used

- **Flask**: A lightweight web framework for Python.
- **SQLite**: A simple database to store data about videos.
- **Whisper**: A machine learning model to transcribe speech.
- **FFmpeg**: Used to convert uploaded videos to DASH format.

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/KittleCodes/VideoVibe.git
   ```

2. Navigate to the project directory:

   ```
   cd VideoVibe
   ```

3. Create a virtual environment (optional but recommended):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

## Usage

1. You can run each microservice using ```python main.py``` in each services /src directory or run the start_services.bat file in the /services directory.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you'd like to contribute to this project.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
