# RC Car Lap Time Tracker with Computer Vision

Empower your RC racing events with an automated, AI-driven lap timing system. This project uses **YOLOv8** (You Only Look Once) to detect RC cars in real-time via webcam or video footage, tracking their positions to automatically record lap times as they cross a user-defined virtual finish line.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Object%20Detection-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## 🏁 Features

*   **AI-Powered Detection**: Uses a custom-trained YOLO model to identify specific cars (e.g., "Blue Car", "Green Car").
*   **Virtual Start/Finish Line**: Draw a finish line directly on the camera feed—no physical sensors/transponders required.
*   **Real-Time HUD**: Displays current lap time, previous laps history, best lap, and penalty status overlaid on the video feed.
*   **Race Control**:
    *   Manual penalty assignment (+2s hotkeys).
    *   Race reset functionality.
    *   CSV Data Export for post-race analysis.
*   **Flexible Input**: Supports both live Webcams and pre-recorded Video files.
*   **Video Recording**: Option to save the annotated race footage for replays.

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/rc-car-lap-tracker.git
    cd rc-car-lap-tracker
    ```

2.  **Set Up Environment**
    It is recommended to use a virtual environment to manage dependencies.

    **Windows:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

    **macOS/Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare the Model**
    Place your trained YOLO model (`.pt` file) in the project directory or update the path in `src/config.py`. By default, it looks for standard YOLO paths or you can specify it via CLI.

## 🚀 Usage

You can run the tracker using the command line interface for maximum flexibility.

### Basic (Webcam)
Run on the default camera (Index 0).
```bash
python run.py
```

### Video File Analysis
Process a pre-recorded race video. The specific flag `-v` triggers "Setup Mode", pausing the first frame so you can draw the finish line.
```bash
python run.py -v "path/to/race_footage.mp4"
```

### Save Output
Record the processed video with the HUD overlay.
```bash
python run.py -c 0 --save --out "my_race_results.mp4"
```

### Full Command Reference
| Argument | Flag | Description | Default |
| :--- | :--- | :--- | :--- |
| Video File | `--video`, `-v` | Path to input video file (overrides webcam) | None |
| Camera Index | `--cam`, `-c` | Webcam index ID | 0 |
| Save Video | `--save`, `-s` | Enable saving processed output | False |
| Output Path | `--out`, `-o` | Filename for saved video | `output_race.mp4` |
| Model Path | `--model`, `-m` | Path to custom YOLO `.pt` file | (Config default) |
| Confidence | `--conf` | Detection confidence threshold (0.0-1.0) | 0.5 |

## 🎮 Controls

Once the application is running:

*   **Draw Finish Line**: Click **Left Mouse Button** twice to set the start (P1) and end (P2) points of the line.
*   **Start Race (Video Mode)**: Press **SPACE** after drawing the line.
*   **Penalties**:
    *   `B`: Add +2s penalty to Blue Car.
    *   `G`: Add +2s penalty to Green Car.
*   **Management**:
    *   `R`: Reset Race (clears laps/times).
    *   `E`: Export Lap Data to CSV.
    *   `Q`: Quit Application.

## 📂 Project Structure

This project follows a modular software engineering approach:

```text
.
├── models/
│   ├── best.pt            # Best version of YoloV11 model
├── run.py                 # Application Entry Point
├── src/
│   ├── config.py          # Configuration & Constants
│   ├── detector.py        # YOLO Model Identification Logic
│   ├── domain.py          # Core Logic (Car state, Finish Line math)
│   ├── race_manager.py    # Main Application Orchestrator
│   └── visualizer.py      # HUD & Drawing Utilities
└── requirements.txt
└── README.md

```

## 📊 Data Export

Pressing `E` during the race will generate individual CSV files for each car in the root directory:
```csv
Lap,Time,Penalty
1,12.45,0.0
2,14.20,2.0
...
```

## 🤝 Contributing & Customization

*   **Adding Entrants**: Edit `src/race_manager.py` to add new cars to the `self.cars` dictionary. Ensure your YOLO model is trained to detect classes matching the dictionary keys.
*   **Tuning**: Adjust `MIN_HISTORY_LENGTH` or `LAP_COOLDOWN_SECONDS` in `src/config.py` if you experience missed laps or double-counting.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
