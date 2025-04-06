# Whisper Subtitle Translator 🎧

Self-hosted UI + FastAPI backend for converting and translating audio into SRT/VTT/JSON subtitles using OpenAI's Whisper.

## ✨ Features
- ⚡️ Real-time subtitle generation with Whisper
- 🌗 Dark/light theme toggle
- 👀 Live preview pane with copy-to-clipboard
- 🌍 Translation support (e.g. ja → en)
- ⬇️ Subtitle download in SRT, VTT, or JSON

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/your-username/whisper-ui.git
cd whisper-ui
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. [Optional] Install `ffmpeg` if not available

If Whisper fails with `ffmpeg not found`, install it from:  
👉 https://ffmpeg.org/download.html

Then, add `ffmpeg` to your system PATH or hardcode it by running:
```bash
which ffmpeg   # (Linux/macOS)
where ffmpeg   # (Windows)
```

Then in your Python file:
```python
import os
os.environ['PATH'] += os.pathsep + "C:/Path/To/ffmpeg/bin"
```

---

### 4. Run the FastAPI server
```bash
uvicorn main:app --reload
```

### 5. Open the UI
Open your browser and navigate to:
```
http://localhost:8000/static/index.html
```

---

## 📄 License
MIT
