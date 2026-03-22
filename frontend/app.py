# frontend/app.py

import sys
import os

# Add the project root to path so we can import services
# This is needed because app.py lives inside frontend/
# but the services folder is one level up
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

import streamlit as st
from services.transcript import get_transcript
from services.chunker import chunk_text
from services.summarizer import summarize
from services.flashcards import generate_flashcards
from services.quiz import generate_quiz


# ─────────────────────────────────────────────
# Page config — must be first Streamlit call
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Knowledge Copilot",
    page_icon="🧠",
    layout="centered"
)


# ─────────────────────────────────────────────
# Initialise session state
# These keys must exist before we try to read them
# ─────────────────────────────────────────────
if "summary" not in st.session_state:
    st.session_state["summary"] = None

if "flashcards" not in st.session_state:
    st.session_state["flashcards"] = None

if "quiz" not in st.session_state:
    st.session_state["quiz"] = None

if "quiz_answers" not in st.session_state:
    st.session_state["quiz_answers"] = {}


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.title("🧠 AI Knowledge Copilot")
st.caption("Paste a YouTube URL to generate a summary, flashcards, and quiz.")

st.divider()


# ─────────────────────────────────────────────
# Input section
# ─────────────────────────────────────────────
url = st.text_input(
    "YouTube URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

generate_btn = st.button("Generate", type="primary", use_container_width=True)


# ─────────────────────────────────────────────
# Generation logic
# Runs when user clicks Generate
# ─────────────────────────────────────────────
if generate_btn and url:

    # Clear previous results
    st.session_state["summary"] = None
    st.session_state["flashcards"] = None
    st.session_state["quiz"] = None
    st.session_state["quiz_answers"] = {}

    try:
        # Step 1: fetch transcript
        with st.spinner("Fetching transcript..."):
            transcript = get_transcript(url)

        st.success(f"Transcript fetched — {len(transcript):,} characters")

        # Step 2: chunk
        with st.spinner("Processing..."):
            chunks = chunk_text(transcript)

        # Step 3: generate all three in parallel
        # We show a spinner for each so user sees progress
        with st.spinner("Generating summary..."):
            summary = summarize(chunks)
            st.session_state["summary"] = summary

        with st.spinner("Generating flashcards..."):
            flashcards = generate_flashcards(chunks)
            st.session_state["flashcards"] = flashcards

        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(chunks)
            st.session_state["quiz"] = quiz

        st.success("Done! See your results in the tabs below.")

    except ValueError as e:
        st.error(f"Invalid URL: {e}")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

elif generate_btn and not url:
    st.warning("Please paste a YouTube URL first.")


# ─────────────────────────────────────────────
# Results tabs
# Only shown after generation is complete
# ─────────────────────────────────────────────
if st.session_state["summary"]:

    st.divider()
    tab1, tab2, tab3 = st.tabs(["📄 Summary", "🃏 Flashcards", "❓ Quiz"])


    # ── Tab 1: Summary ──────────────────────
    with tab1:
        st.markdown(st.session_state["summary"])


    # ── Tab 2: Flashcards ───────────────────
    with tab2:
        flashcards = st.session_state["flashcards"]

        if not flashcards:
            st.info("No flashcards generated.")
        else:
            st.caption(f"{len(flashcards)} flashcards generated")

            for i, card in enumerate(flashcards):
                # Each flashcard is an expander
                # Closed = shows question, open = shows answer
                with st.expander(f"Card {i+1}: {card['front']}"):
                    st.markdown(f"**Answer:** {card['back']}")


    # ── Tab 3: Quiz ─────────────────────────
    with tab3:
        questions = st.session_state["quiz"]

        if not questions:
            st.info("No quiz generated.")
        else:
            st.caption(f"{len(questions)} questions")

            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}: {q['question']}**")

                # Radio button for answer selection
                # key must be unique per question
                selected = st.radio(
                    label=f"q{i}",
                    options=q["options"],
                    index=None,          # nothing selected by default
                    label_visibility="collapsed",
                    key=f"quiz_q_{i}"
                )

                if selected:
                    if selected == q["answer"]:
                        st.success(f"Correct! {q['explanation']}")
                    else:
                        st.error(
                            f"Not quite. The correct answer is: "
                            f"**{q['answer']}**\n\n{q['explanation']}"
                        )

                st.divider()