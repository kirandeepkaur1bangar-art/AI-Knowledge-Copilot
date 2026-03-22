import os
from llm import ask_llm


# ─────────────────────────────────────────────
# Load the prompt template from file
# Why from a file and not hardcoded here?
# Because prompts change often during development.
# Keeping them in .txt files means you can tweak
# the prompt without touching Python code at all.
# ─────────────────────────────────────────────

def load_prompt(filename: str) -> str:
    """Load a prompt template from the prompts/ folder."""
    prompt_path = os.path.join(
        os.path.dirname(__file__),  # current file's directory
        "..",                        # go up one level
        "prompts",                   # into prompts folder
        filename                     # the file we want
    )
    with open(prompt_path, "r") as f:
        return f.read()


# ─────────────────────────────────────────────
# Token estimation
# Groq's limit is ~6000 tokens per call
# 1 token ≈ 4 characters (rough estimate)
# So 6000 tokens ≈ 24000 characters max per call
# ─────────────────────────────────────────────

MAX_CHARS_PER_CALL = 20000  # safe limit, below the token ceiling


def summarize(chunks: list[str]) -> str:
    """
    Takes a list of transcript chunks and returns a summary.

    For short transcripts — joins all chunks, one AI call.
    For long transcripts — summarises in batches, then
    summarises those summaries (hierarchical summarisation).

    Parameters:
        chunks: list of text chunks from chunker.py

    Returns:
        summary string
    """

    prompt_template = load_prompt("summary.txt")

    # Join all chunks into one string
    full_text = " ".join(chunks)

    if len(full_text) <= MAX_CHARS_PER_CALL:
        # ── Short transcript: one call ──────────────────
        # Replace {transcript} placeholder with actual text
        prompt = prompt_template.replace("{transcript}", full_text)
        return ask_llm(prompt)

    else:
        # ── Long transcript: hierarchical summarisation ──
        print("  Long transcript detected — using hierarchical summarisation")

        # Step 1: split into batches and summarise each
        mini_summaries = []
        batch = []
        batch_size = 0

        for chunk in chunks:
            if batch_size + len(chunk) > MAX_CHARS_PER_CALL:
                # batch is full — summarise it
                batch_text = " ".join(batch)
                prompt = prompt_template.replace("{transcript}", batch_text)
                mini_summary = ask_llm(prompt)
                mini_summaries.append(mini_summary)
                print(f"  Summarised batch of {len(batch)} chunks")

                # start a new batch
                batch = [chunk]
                batch_size = len(chunk)
            else:
                batch.append(chunk)
                batch_size += len(chunk)

        # don't forget the last batch
        if batch:
            batch_text = " ".join(batch)
            prompt = prompt_template.replace("{transcript}", batch_text)
            mini_summary = ask_llm(prompt)
            mini_summaries.append(mini_summary)

        # Step 2: summarise the mini summaries into one final summary
        print(f"  Combining {len(mini_summaries)} mini summaries...")
        combined = "\n\n---\n\n".join(mini_summaries)
        final_prompt = f"""You are given several summaries of different parts of a video.
Combine them into one cohesive final summary with these sections:
Overview, Key Concepts, Main Takeaways, Prerequisites.

Summaries:
{combined}"""

        return ask_llm(final_prompt)
    