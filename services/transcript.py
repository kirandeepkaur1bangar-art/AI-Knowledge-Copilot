# services/transcript.py

import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound
)


# ─────────────────────────────────────────────
# PART 1: Extract video ID from any URL format
# ─────────────────────────────────────────────

def extract_video_id(url: str) -> str:
    """
    Handles all YouTube URL formats:
    1. https://www.youtube.com/watch?v=dQw4w9WgXcQ
    2. https://youtu.be/dQw4w9WgXcQ
    3. https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s&list=xyz
    """
    pattern = r"(?:v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)

    if not match:
        raise ValueError(f"Could not find a valid YouTube video ID in: {url}")

    return match.group(1)


# ─────────────────────────────────────────────
# PART 2: Path A — fetch YouTube captions
# ─────────────────────────────────────────────

def get_transcript_from_captions(video_id: str) -> str:
    """
    Fetches YouTube captions.
    Uses proxy on cloud deployments to avoid IP blocks.
    """
    import os

    ytt_api = YouTubeTranscriptApi()

    # Check if running on cloud (Streamlit Cloud sets this)
    is_cloud = os.getenv("IS_CLOUD", "false").lower() == "true"

    try:
        if is_cloud:
            # Use webshare proxy on cloud
            from youtube_transcript_api.proxies import WebshareProxyConfig
            proxy_config = WebshareProxyConfig(
                proxy_username=os.getenv("PROXY_USERNAME"),
                proxy_password=os.getenv("PROXY_PASSWORD"),
            )
            ytt_api = YouTubeTranscriptApi(proxies=proxy_config)

        fetched = ytt_api.fetch(video_id)

    except NoTranscriptFound:
        transcript_list = ytt_api.list(video_id)
        available = list(transcript_list)
        if not available:
            raise NoTranscriptFound(video_id, [], {})
        fetched = available[0].fetch()
        print(f"  No English captions — using: {available[0].language}")

    full_text = " ".join([snippet.text for snippet in fetched])
    return full_text
# ─────────────────────────────────────────────
# PART 3: Path B — download audio + Whisper
# ─────────────────────────────────────────────

def get_transcript_from_whisper(video_id: str) -> str:
    """
    Downloads audio from YouTube and transcribes locally with Whisper.
    Used as fallback when captions don't exist.
    Automatically tries multiple browsers for cookies.
    """

    import yt_dlp
    import whisper

    audio_path = f"/tmp/{video_id}.mp3"

    base_opts = {
        "outtmpl": f"/tmp/{video_id}",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "quiet": True,
        "format": "bestaudio/best/worstaudio/worst",
    }

    # Try browsers in order until one works
    browsers = ["chrome", "firefox", "chromium", "edge", "safari"]
    downloaded = False

    for browser in browsers:
        try:
            print(f"  Trying cookies from {browser}...")
            opts = {
                **base_opts,
                "cookiesfrombrowser": (browser,),
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            print(f"  Download succeeded using {browser} cookies.")
            downloaded = True
            break
        except Exception as e:
            print(f"  {browser} failed: {e}")
            continue

    # Last resort — try without cookies
    if not downloaded:
        print("  Trying without cookies...")
        try:
            with yt_dlp.YoutubeDL(base_opts) as ydl:
                ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
            downloaded = True
        except Exception:
            raise ValueError(
                "Could not download this video. YouTube is blocking "
                "automated downloads. Please either:\n"
                "1. Try a different video\n"
                "2. Download the audio manually and use the "
                "'Audio File' upload option instead."
            )

    # Transcribe with Whisper
    print("  Transcribing with Whisper...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    # Clean up temp file
    if os.path.exists(audio_path):
        os.remove(audio_path)
        print("  Temp file cleaned up.")

    return result["text"]


# ─────────────────────────────────────────────
# PART 4: Audio file upload path
# ─────────────────────────────────────────────

def get_transcript_from_audio_file(audio_bytes: bytes, filename: str) -> str:
    """
    Transcribes an uploaded audio file using Whisper.
    Used when user uploads their own audio in the UI.
    No YouTube involved — always works.
    """

    import whisper
    import tempfile

    suffix = os.path.splitext(filename)[1]

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    print(f"  Transcribing uploaded file: {filename}")

    try:
        model = whisper.load_model("base")
        result = model.transcribe(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            print("  Temp file cleaned up.")

    return result["text"]


# ─────────────────────────────────────────────
# PART 5: Main function — only thing other files call
# ─────────────────────────────────────────────

def get_transcript(url: str) -> str:
    """
    THE only function the rest of the app calls for YouTube URLs.

    Tries captions first — fast and free.
    Falls back to Whisper if captions are disabled.
    Shows clear error if both fail.
    """

    video_id = extract_video_id(url)
    print(f"  Video ID: {video_id}")

    try:
        print("  Fetching captions...")
        transcript = get_transcript_from_captions(video_id)
        print(f"  Done. Got {len(transcript)} characters.")
        return transcript

    except (TranscriptsDisabled, NoTranscriptFound):
        print("  No captions found. Trying Whisper fallback...")
        return get_transcript_from_whisper(video_id)
