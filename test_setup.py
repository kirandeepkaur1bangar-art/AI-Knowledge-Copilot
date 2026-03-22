# test_setup.py
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing imports...")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("  youtube-transcript-api ✓")
except ImportError as e:
    print(f"  youtube-transcript-api ✗ — {e}")

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("  langchain-text-splitters ✓")
except ImportError as e:
    print(f"  langchain-text-splitters ✗ — {e}")

try:
    from groq import Groq
    print("  groq ✓")
except ImportError as e:
    print(f"  groq ✗ — {e}")

try:
    import streamlit
    print("  streamlit ✓")
except ImportError as e:
    print(f"  streamlit ✗ — {e}")

# Test API key
print("\nTesting API key...")
api_key = os.getenv("GROQ_API_KEY")
if api_key and api_key.startswith("gsk_"):
    print(f"  GROQ_API_KEY loaded ✓  ({api_key[:12]}...)")
else:
    print("  GROQ_API_KEY not found ✗ — check your .env file")

# Test actual Groq call
print("\nTesting Groq API call...")
try:
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Reply with exactly: setup works"}],
        max_tokens=16
    )
    reply = response.choices[0].message.content
    print(f"  Groq says: {reply} ✓")
except Exception as e:
    print(f"  Groq API call failed ✗ — {e}")

print("\nAll done. Ready to build.")