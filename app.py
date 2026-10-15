import os
import re
import datetime
import streamlit as st
import yt_dlp
import whisper
import srt
import webvtt

# Page setup
st.set_page_config(page_title="Instagram Reels Transcription Studio", page_icon="🎙️", layout="wide")

AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@st.cache_resource
def load_whisper_model(model_name: str):
    return whisper.load_model(model_name)

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_audio(url: str) -> tuple[str, str]:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_template = os.path.join(AUDIO_DIR, f"reel_{timestamp}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', f"reel_{timestamp}")
        audio_path = os.path.join(AUDIO_DIR, f"reel_{timestamp}.mp3")
        
    return audio_path, sanitize_filename(video_title)

def format_timestamp(seconds: float) -> str:
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# UI Header
st.title("🎙️ Instagram Reels Transcription Studio")
st.caption("Convert Instagram Reels into clean, structured transcripts with timestamps.")

# Model selection
model_size = st.sidebar.selectbox("Select Whisper AI Model", ["tiny", "base", "small", "medium"], index=2)

# Input Box
url = st.text_input("Paste Instagram Reel Link:", placeholder="https://www.instagram.com/reel/...")

if st.button("Transcribe Reel", type="primary"):
    if not url or "instagram.com" not in url:
        st.error("Please enter a valid Instagram URL.")
    else:
        try:
            with st.spinner("Downloading audio from Instagram..."):
                audio_path, title = download_audio(url)
                
            with st.spinner(f"Transcribing audio using Whisper '{model_size}' model..."):
                model = load_whisper_model(model_size)
                result = model.transcribe(audio_path)
                
            st.success("Transcription Complete!")
            
            # Display Full Text
            st.subheader("Full Transcript")
            st.write(result['text'].strip())
            
            # Display Timestamps
            st.subheader("Timestamp Breakdown")
            for segment in result['segments']:
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = segment['text'].strip()
                st.markdown(f"`[{start} ➔ {end}]` {text}")
                
            # Cleanup temp file
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
        except Exception as e:
            st.error(f"Error processing video: {e}")
