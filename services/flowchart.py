# services/flowchart.py

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


def clean_mermaid(response: str) -> str:
    """
    Clean and fix Mermaid syntax from LLM response.
    Handles missing line breaks, markdown blocks, and formatting issues.
    """
    import re

    cleaned = response.strip()

    # Remove markdown code blocks if present
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
    if cleaned.endswith("```"):
        cleaned = cleaned.rsplit("\n", 1)[0]

    cleaned = cleaned.strip()

    # Fix all-on-one-line issue
    # Insert newline before every node definition and arrow
    # Pattern: space followed by a capital letter that starts a node
    cleaned = re.sub(r'\s{2,}([A-Z]\w*[\[\(\{])', r'\n    \1', cleaned)

    # Also handle "graph TD" being on same line as first node
    cleaned = re.sub(r'(graph TD)\s+([A-Z])', r'\1\n    \2', cleaned)

    # Fix edge labels that got split across lines
    # Rejoin lines that are part of |label| 
    lines = cleaned.split('\n')
    fixed_lines = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if buffer:
            # We're collecting parts of a split line
            buffer += " " + stripped
            # Check if the label is now complete (has closing |)
            if buffer.count('|') % 2 == 0:
                fixed_lines.append("    " + buffer.strip())
                buffer = ""
        else:
            # Check if this line has an unclosed |
            if stripped.count('|') % 2 != 0:
                buffer = stripped
            else:
                if stripped.startswith('graph'):
                    fixed_lines.append(stripped)
                else:
                    fixed_lines.append("    " + stripped)

    if buffer:
        fixed_lines.append("    " + buffer.strip())

    result = "\n".join(fixed_lines)

    # Final cleanup — remove any double spaces inside brackets
    result = re.sub(r'\[\s+', '[', result)
    result = re.sub(r'\s+\]', ']', result)

    return result.strip()


def generate_flowchart(chunks: list[str]) -> str:
    """
    Takes transcript chunks and returns Mermaid.js diagram syntax.

    Parameters:
        chunks: list of text chunks from chunker.py

    Returns:
        Mermaid syntax string starting with "graph TD"
    """

    prompt_template = load_prompt("flowchart.txt")

    # For flowcharts we want the full picture
    # so join all chunks and trim if too long
    full_text = " ".join(chunks)
    if len(full_text) > 20000:
        full_text = full_text[:20000]
        print("  Transcript trimmed for flowchart generation")

    prompt = prompt_template.replace("{transcript}", full_text)

    print("  Asking Groq for flowchart...")
    response = ask_llm(prompt)

    mermaid_code = clean_mermaid(response)

    # Basic validation — must start with graph
    if not mermaid_code.startswith("graph"):
        print(f"  Warning: unexpected response:\n{mermaid_code[:200]}")

    print("  Flowchart generated")
    return mermaid_code
