# services/quiz.py

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
    Strips markdown code blocks if present.
    """
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("\n", 1)[0]

    return json.loads(cleaned.strip())


def generate_quiz(chunks: list[str]) -> list[dict]:
    """
    Takes transcript chunks and returns a list of quiz question dicts.

    Each dict has:
        question:    the question text
        options:     list of 4 answer choices
        answer:      the correct option (matches exactly one in options)
        explanation: why the answer is correct

    Parameters:
        chunks: list of text chunks from chunker.py

    Returns:
        list of quiz question dicts
    """

    prompt_template = load_prompt("quiz.txt")

    # Join and trim same as flashcards
    full_text = " ".join(chunks)
    if len(full_text) > 20000:
        full_text = full_text[:20000]
        print("  Transcript trimmed to 20000 chars for quiz generation")

    prompt = prompt_template.replace("{transcript}", full_text)

    print("  Asking Groq for quiz questions...")
    response = ask_llm(prompt)

    try:
        questions = parse_json_response(response)
        print(f"  Got {len(questions)} questions")
        return questions

    except json.JSONDecodeError as e:
        print(f"  JSON parse failed: {e}")
        print(f"  Raw response was:\n{response}")
        return []
    