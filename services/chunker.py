from langchain_text_splitters import RecursiveCharacterTextSplitter


# ─────────────────────────────────────────────
# Why RecursiveCharacterTextSplitter?
#
# It tries to split in this priority order:
# 1. paragraphs (\n\n)  — best split point
# 2. sentences (\n)     — second best
# 3. words (space)      — last resort
#
# This means it never cuts mid-sentence if it
# can avoid it. Much smarter than splitting
# every N characters blindly.
# ─────────────────────────────────────────────

def chunk_text(text: str) -> list[str]:
    """
    Splits a long transcript into overlapping chunks.

    Parameters:
        text: the full transcript string

    Returns:
        list of chunk strings, ready to send to AI
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        # each chunk is max 1500 characters
        # why 1500? big enough for meaningful context,
        # small enough to be focused and cheap

        chunk_overlap=200,
        # last 200 chars of each chunk are repeated
        # at the start of the next chunk
        # prevents concepts being split across boundaries

        length_function=len,
        # how to measure chunk size — just count characters

        separators=["\n\n", "\n", " ", ""]
        # try splitting on these in order:
        # paragraph break → line break → space → anywhere
    )

    chunks = splitter.split_text(text)

    return chunks

