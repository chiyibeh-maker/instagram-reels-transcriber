# 🎙️ Instagram Reels Transcription Studio

An open-source CLI studio that extracts audio from public Instagram Reels and generates accurate, timestamped transcriptions locally using OpenAI's **Whisper** model.

Inspired by tools like Saveto AI, this tool downloads audio streams, auto-detects language, generates precise word/sentence timestamps, and exports transcripts in `.txt`, `.srt`, and `.vtt` formats.

---

## 🌟 Features

- 🔗 **Direct URL Input**: Paste any public Instagram Reel URL to instantly process audio.
- ⏱️ **Timestamp Breakdown**: Displays start and end times for every spoken line.
- 🌐 **90+ Languages**: Automatically detects and transcribes speech across dozens of languages.
- 📁 **Multi-Format Export**: Generates `.txt`, `.srt` (Subtitles), and `.vtt` (WebVTT) files automatically.
- 🔒 **Privacy-First & Free**: Runs 100% locally on your machine—no API keys or subscriptions required.

---

## 🛠️ Prerequisites

1. **Python 3.9+** installed on your machine.
2. **FFmpeg** installed and available in your system's `PATH`:
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt install ffmpeg`
   - **Windows**: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/).

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/chiyibeh-maker/instagram-reels-transcriber.git
cd instagram-reels-transcriber
```

### 2. Set Up a Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Studio
```bash
python app.py
```

---

## 📂 Output Structure

After transcribing a reel, output files are saved in the `transcripts/` directory:

```text
transcripts/
├── Reel_Title_20261015.txt   # Plain text transcript with timestamps
├── Reel_Title_20261015.srt   # Subtitle file for video editors
└── Reel_Title_20261015.vtt   # WebVTT file for web players
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.