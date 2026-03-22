# services/mom.py

import os
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


def generate_mom(chunks: list[str]) -> str:
    """
    Takes meeting transcript chunks and returns
    a structured Minutes of Meeting document.

    Parameters:
        chunks: list of text chunks from chunker.py

    Returns:
        formatted MoM string with all sections
    """

    prompt_template = load_prompt("mom.txt")

    # Join all chunks — MoM needs full context
    # to correctly attribute owners and decisions
    full_text = " ".join(chunks)

    if len(full_text) > 20000:
        full_text = full_text[:20000]
        print("  Transcript trimmed for MoM generation")

    prompt = prompt_template.replace("{transcript}", full_text)

    print("  Generating MoM...")
    response = ask_llm(prompt)

    return response