import os
import re
import sys
import datetime
import yt_dlp
import whisper
import srt
import webvtt
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

# Directories
AUDIO_DOWNLOAD_DIR = "temp_audio"
TRANSCRIPT_OUTPUT_DIR = "transcripts"
DEFAULT_WHISPER_MODEL = "small"

os.makedirs(AUDIO_DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_OUTPUT_DIR, exist_ok=True)

console = Console()

def sanitize_filename(name: str) -> str:
    """Sanitize strings for filesystem-safe filenames."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_audio(url: str) -> tuple[str, str]:
    """Downloads audio from an Instagram Reel URL using yt-dlp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_template = os.path.join(AUDIO_DOWNLOAD_DIR, f"reel_{timestamp}.%(ext)s")

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

    with Progress(SpinnerColumn(), TextColumn("[bold cyan]Fetching Instagram Reel audio..."), console=console) as progress:
        progress.add_task("download", total=None)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', f"reel_{timestamp}")
            audio_path = os.path.join(AUDIO_DOWNLOAD_DIR, f"reel_{timestamp}.mp3")

    return audio_path, sanitize_filename(video_title)

def format_timestamp(seconds: float) -> str:
    """Formats seconds into HH:MM:SS string."""
    td = datetime.timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def transcribe_audio(audio_path: str, model_name: str = DEFAULT_WHISPER_MODEL) -> dict:
    """Transcribes audio using OpenAI Whisper locally."""
    with Progress(SpinnerColumn(), TextColumn(f"[bold green]Loading Whisper model ('{model_name}')..."), console=console) as progress:
        progress.add_task("load", total=None)
        model = whisper.load_model(model_name)

    with Progress(SpinnerColumn(), TextColumn("[bold yellow]Transcribing audio & generating timestamps..."), console=console) as progress:
        progress.add_task("transcribe", total=None)
        result = model.transcribe(audio_path, verbose=False)

    return result

def save_exports(result: dict, base_filename: str):
    """Exports the transcription to .txt, .srt, and .vtt formats."""
    base_path = os.path.join(TRANSCRIPT_OUTPUT_DIR, base_filename)

    # 1. TXT Export
    txt_path = f"{base_path}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"--- TRANSCRIPT FOR: {base_filename} ---\n\n")
        for segment in result['segments']:
            start = format_timestamp(segment['start'])
            end = format_timestamp(segment['end'])
            text = segment['text'].strip()
            f.write(f"[{start} --> {end}] {text}\n")

    # 2. SRT Subtitle Export
    srt_path = f"{base_path}.srt"
    srt_subtitles = []
    for idx, segment in enumerate(result['segments'], start=1):
        start_td = datetime.timedelta(seconds=segment['start'])
        end_td = datetime.timedelta(seconds=segment['end'])
        srt_subtitles.append(
            srt.Subtitle(index=idx, start=start_td, end=end_td, content=segment['text'].strip())
        )
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt.compose(srt_subtitles))

    # 3. WebVTT Export
    vtt_path = f"{base_path}.vtt"
    vtt = webvtt.WebVTT()
    for segment in result['segments']:
        start = format_timestamp(segment['start']) + ".000"
        end = format_timestamp(segment['end']) + ".000"
        vtt.captions.append(webvtt.Caption(start, end, segment['text'].strip()))
    vtt.save(vtt_path)

    return txt_path, srt_path, vtt_path

def cleanup(file_path: str):
    """Removes temporary downloaded audio files."""
    if os.path.exists(file_path):
        os.remove(file_path)

def main():
    console.print(Panel.fit(
        "[bold magenta]Instagram Reels Transcription Studio[/bold magenta]\n"
        "[dim]Paste any public IG Reel URL to generate instant timestamped transcripts.[/dim]",
        border_style="magenta"
    ))

    while True:
        url = Prompt.ask("\n[bold cyan]Paste Instagram Reel Link[/bold cyan] (or type 'exit' to quit)")
        
        if url.lower().strip() in ['exit', 'quit', 'q']:
            console.print("[yellow]Exiting Studio. Goodbye![/yellow]")
            sys.exit(0)

        if "instagram.com" not in url:
            console.print("[bold red]Error:[/bold red] Please enter a valid Instagram link.")
            continue

        audio_path = None
        try:
            audio_path, title = download_audio(url)
            result = transcribe_audio(audio_path)

            console.print("\n[bold green]✓ Transcription Complete![/bold green]\n")
            console.print(Panel(result['text'].strip(), title="[bold]Full Text Output[/bold]", border_style="green"))
            
            console.print("\n[bold]Timestamped Breakdown:[/bold]")
            for segment in result['segments']:
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                console.print(f"[dim cyan][{start} ➔ {end}][/dim cyan] {segment['text'].strip()}")

            txt_p, srt_p, vtt_p = save_exports(result, title)
            console.print(f"\n[bold green]Files Generated:[/bold green]")
            console.print(f" • Plain Text: [yellow]{txt_p}[/yellow]")
            console.print(f" • Subtitles (SRT): [yellow]{srt_p}[/yellow]")
            console.print(f" • WebVTT: [yellow]{vtt_p}[/yellow]")

        except Exception as e:
            console.print(f"[bold red]An error occurred:[/bold red] {e}")

        finally:
            if audio_path:
                cleanup(audio_path)

if __name__ == "__main__":
    main()