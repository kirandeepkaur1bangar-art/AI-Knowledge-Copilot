# services/llm.py

import os
from groq import Groq
from dotenv import load_dotenv

# Load .env file so os.getenv() can find our keys
# This needs to run before anything else
load_dotenv()

# ─────────────────────────────────────────────
# Model name in ONE place
# ─────────────────────────────────────────────
#MODEL = "llama-3.3-70b-versatile"
MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

# ─────────────────────────────────────────────
# The only function the rest of the app ever calls
# ─────────────────────────────────────────────
def ask_llm(prompt: str) -> str:
    """
    Send a prompt to Groq, get a text response back.

    That's the entire job of this function.
    Every other service just calls ask_llm("...") and
    gets a plain string back — clean and simple.

    Parameters:
        prompt: the full instruction + content we send to the AI

    Returns:
        the AI's response as a plain string
    """

    # Create the Groq client
    # It reads GROQ_API_KEY from environment automatically
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # Send the prompt to the model
    # messages format: list of dicts with "role" and "content"
    # role "user" = we are talking to the AI
    # role "assistant" = the AI's previous responses (not needed here)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        # temperature controls creativity vs consistency:
        # 0.0 = very consistent, almost identical responses every time
        # 1.0 = very creative, different every time
        # 0.3 = mostly consistent with slight variation — good for our use case
        max_tokens=4096,
        # max_tokens = maximum length of response
        # 4096 is enough for a detailed summary + flashcards
    )

    # Extract just the text from the response object
    # response.choices[0].message.content is where Groq puts the actual text
    return response.choices[0].message.content
