# services/transcript.py

import re
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)


# ─────────────────────────────────────────────
# PART 1: Extract video ID from any URL format
# ─────────────────────────────────────────────

def extract_video_id(url: str) -> str:
    """
    YouTube URLs come in 3 formats — we handle all of them:

    1. https://www.youtube.com/watch?v=dQw4w9WgXcQ
    2. https://youtu.be/dQw4w9WgXcQ
    3. https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s

    We use regex to find the 11-character video ID in any of these.
    YouTube video IDs are always exactly 11 characters.
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
    Fetches YouTube's own captions for the video.
    Updated to use the new youtube-transcript-api syntax.
    """

    # New API: create an instance first, then fetch
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id)

    # fetched is a FetchedTranscript object
    # iterate over it to get text snippets
    full_text = " ".join([snippet.text for snippet in fetched])

    return full_text


# ─────────────────────────────────────────────
# PART 3: Path B — Whisper fallback
# ─────────────────────────────────────────────

def get_transcript_from_whisper(video_id: str) -> str:
    """
    Fallback when captions don't exist.
    Downloads audio and transcribes locally with Whisper.

    We skipped Whisper install for now — this raises a
    helpful error instead of crashing silently.
    """

    raise NotImplementedError(
        "This video has no captions. "
        "Whisper fallback is not set up yet — "
        "try a video that has captions enabled."
    )


# ─────────────────────────────────────────────
# PART 4: Main function — only thing other files call
# ─────────────────────────────────────────────

def get_transcript(url: str) -> str:
    """
    THE only function the rest of the app calls.

    Pass in any YouTube URL, get back plain text.
    Handles all URL formats, tries captions first,
    falls back to Whisper if needed.
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
    
