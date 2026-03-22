# services/flashcards.py

import os
import json
from llm import ask_llm


def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts/ folder."""
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "prompts",
        filename
    )
    with open(prompt_path, "r") as f:
        return f.read()


def parse_json_response(response: str) -> list:
    """
    Safely parse JSON from LLM response.

    Why do we need this?
    Sometimes the AI wraps JSON in markdown code blocks:
```json
      [{"front": ...}]
```
    We strip those before parsing.
    """

    # Strip markdown code blocks if present
    cleaned = response.strip()
    if cleaned.startswith("```"):
        # remove first line (```json or ```)
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        # remove last line
        cleaned = cleaned.rsplit("\n", 1)[0]

    return json.loads(cleaned.strip())


def generate_flashcards(chunks: list[str]) -> list[dict]:
    """
    Takes transcript chunks and returns a list of flashcard dicts.

    Each dict has:
        front: the question
        back:  the answer

    Parameters:
        chunks: list of text chunks from chunker.py

    Returns:
        list of {"front": "...", "back": "..."} dicts
    """

    prompt_template = load_prompt("flashcards.txt")

    # Join chunks — for flashcards we want the full context
    # so the AI picks the most important concepts overall
    full_text = " ".join(chunks)

    # If too long, trim to safe limit
    # For flashcards we care about concepts, not every detail
    if len(full_text) > 20000:
        full_text = full_text[:20000]
        print("  Transcript trimmed to 20000 chars for flashcard generation")

    prompt = prompt_template.replace("{transcript}", full_text)

    print("  Asking Groq for flashcards...")
    response = ask_llm(prompt)

    # Parse the JSON response
    try:
        flashcards = parse_json_response(response)
        print(f"  Got {len(flashcards)} flashcards")
        return flashcards

    except json.JSONDecodeError as e:
        # If JSON parsing fails, print what the AI returned
        # so we can debug the prompt
        print(f"  JSON parse failed: {e}")
        print(f"  Raw response was:\n{response}")
        return []
    

# ─────────────────────────────────────────────
# Quick test — delete after confirming it works
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(__file__))

    from transcript import get_transcript
    from chunker import chunk_text

    url = "https://www.youtube.com/watch?v=aircAruvnKk"

    print("Fetching transcript...")
    transcript = get_transcript(url)

    print("Chunking...")
    chunks = chunk_text(transcript)

    print("Generating flashcards...")
    flashcards = generate_flashcards(chunks)

    print("\n─── FLASHCARDS ───")
    for i, card in enumerate(flashcards, 1):
        print(f"\nCard {i}:")
        print(f"  Q: {card['front']}")
        print(f"  A: {card['back']}")