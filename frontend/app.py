# frontend/app.py

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "services"))

import streamlit as st
from services.transcript import get_transcript
from services.chunker import chunk_text
from services.summarizer import summarize
from services.flashcards import generate_flashcards
from services.quiz import generate_quiz
from services.flowchart import generate_flowchart
from services.rag import build_index, answer_question
from services.pdf_export import generate_pdf


# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Knowledge Copilot",
    page_icon="🧠",
    layout="centered"
)


# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main .block-container {
        max-width: 800px;
        padding-top: 2rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .knowledge-card {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .knowledge-card:hover {
        border-color: rgba(128,128,128,0.4);
    }
    .stat-container {
        display: flex;
        gap: 12px;
        margin: 16px 0;
    }
    .stat-box {
        flex: 1;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.2);
    }
    .stat-number {
        font-size: 22px;
        font-weight: 600;
        color: #4A90D9;
    }
    .stat-label {
        font-size: 11px;
        color: gray;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge {
        display: inline-block;
        background: #EEF2FF;
        color: #4338CA;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .stRadio > div {
        gap: 8px;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
    }
    .streamlit-expanderHeader {
        border-radius: 8px;
        font-weight: 500;
    }
    hr {
        margin: 1.5rem 0;
        border-color: rgba(128,128,128,0.15);
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
for key in ["summary", "flashcards", "quiz", "flowchart"]:
    if key not in st.session_state:
        st.session_state[key] = None

if "quiz_answers" not in st.session_state:
    st.session_state["quiz_answers"] = {}

if "rag_ready" not in st.session_state:
    st.session_state["rag_ready"] = False

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "transcript" not in st.session_state:
    st.session_state["transcript"] = None

if "chunks" not in st.session_state:
    st.session_state["chunks"] = None

if "url" not in st.session_state:
    st.session_state["url"] = None


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown(
    '<div style="text-align:center; margin-bottom:8px;">'
    '<span class="badge">AI Powered</span></div>',
    unsafe_allow_html=True
)
st.markdown(
    '<h1 style="text-align:center; font-size:2.2rem; margin-bottom:8px;">'
    '🧠 Knowledge Copilot</h1>',
    unsafe_allow_html=True
)
st.markdown(
    '<p style="text-align:center; color:gray; margin-bottom:32px;">'
    'Transform any content into structured, actionable knowledge</p>',
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
# Mode selector
# ─────────────────────────────────────────────
mode = st.radio(
    "Select mode",
    ["🎓 Learning Mode", "💼 Meeting Mode"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()


# ─────────────────────────────────────────────
# LEARNING MODE
# ─────────────────────────────────────────────
if mode == "🎓 Learning Mode":

    # Input type
    input_mode = st.radio(
        "Input type",
        ["🔗 YouTube URL", "🎵 Audio File"],
        horizontal=True
    )

    url = None
    uploaded_file = None

    if input_mode == "🔗 YouTube URL":
        url = st.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=["mp3", "mp4", "wav", "m4a", "ogg"],
            help="Supported: MP3, MP4, WAV, M4A, OGG"
        )

    generate_btn = st.button(
        "Generate Learning Materials",
        type="primary",
        use_container_width=True
    )

    if generate_btn:

        # Clear previous results
        for key in ["summary", "flashcards", "quiz", "flowchart"]:
            st.session_state[key] = None
        st.session_state["quiz_answers"] = {}
        st.session_state["rag_ready"] = False
        st.session_state["chat_history"] = []
        st.session_state["transcript"] = None
        st.session_state["chunks"] = None
        st.session_state["url"] = url

        try:
            # Get transcript
            if input_mode == "🔗 YouTube URL":
                if not url:
                    st.warning("Please paste a YouTube URL first.")
                    st.stop()
                with st.spinner("Fetching transcript..."):
                    transcript = get_transcript(url)
            else:
                if not uploaded_file:
                    st.warning("Please upload an audio file first.")
                    st.stop()
                with st.spinner(
                    f"Transcribing {uploaded_file.name} with Whisper..."
                ):
                    from services.transcript import get_transcript_from_audio_file
                    transcript = get_transcript_from_audio_file(
                        uploaded_file.read(),
                        uploaded_file.name
                    )

            st.session_state["transcript"] = transcript

            # Chunk
            with st.spinner("Processing..."):
                chunks = chunk_text(transcript)
                st.session_state["chunks"] = chunks

            # Generate all outputs
            with st.spinner("Generating summary..."):
                st.session_state["summary"] = summarize(chunks)

            with st.spinner("Generating flashcards..."):
                st.session_state["flashcards"] = generate_flashcards(chunks)

            with st.spinner("Generating quiz..."):
                st.session_state["quiz"] = generate_quiz(chunks)

            with st.spinner("Generating flowchart..."):
                st.session_state["flowchart"] = generate_flowchart(chunks)

            with st.spinner("Building knowledge index..."):
                build_index(chunks)
                st.session_state["rag_ready"] = True
                st.session_state["chat_history"] = []

            st.success("Done!")

            # Stats bar
            st.markdown(f"""
            <div class="stat-container">
                <div class="stat-box">
                    <div class="stat-number">{len(transcript):,}</div>
                    <div class="stat-label">Characters</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{len(chunks)}</div>
                    <div class="stat-label">Chunks</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">
                        {len(st.session_state["flashcards"] or [])}
                    </div>
                    <div class="stat-label">Flashcards</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">
                        {len(st.session_state["quiz"] or [])}
                    </div>
                    <div class="stat-label">Questions</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        except ValueError as e:
            st.error(f"Invalid URL: {e}")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    # ── Results ──────────────────────────────
    if st.session_state["summary"]:

        st.divider()

        # Tab navigation — persists across reruns
        selected_tab = st.radio(
            "View",
            ["📄 Summary", "🃏 Flashcards", "❓ Quiz", "🔀 Flowchart"],
            horizontal=True,
            label_visibility="collapsed",
            key="tab_selector"
        )

        st.divider()

        # ── Summary ─────────────────────────
        if selected_tab == "📄 Summary":
            st.markdown(st.session_state["summary"])

        # ── Flashcards ───────────────────────
        elif selected_tab == "🃏 Flashcards":
            flashcards = st.session_state["flashcards"]
            if not flashcards:
                st.info("No flashcards generated.")
            else:
                st.caption(
                    f"{len(flashcards)} flashcards — click to reveal answer"
                )
                for i, card in enumerate(flashcards):
                    with st.expander(f"Card {i+1} — {card['front']}"):
                        st.markdown(f"""
                        <div class="knowledge-card">
                            <div style="font-size:11px; text-transform:uppercase;
                                letter-spacing:0.05em; color:gray;
                                margin-bottom:6px;">Answer</div>
                            <div style="font-size:15px; line-height:1.6;">
                                {card['back']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

        # ── Quiz ─────────────────────────────
        elif selected_tab == "❓ Quiz":
            questions = st.session_state["quiz"]
            if not questions:
                st.info("No quiz generated.")
            else:
                st.caption(f"{len(questions)} questions")
                for i, q in enumerate(questions):
                    st.markdown(f"""
                    <div class="knowledge-card">
                        <div style="font-size:15px; font-weight:500;
                            margin-bottom:4px;">
                            Q{i+1}: {q['question']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    selected = st.radio(
                        label=f"q{i}",
                        options=q["options"],
                        index=None,
                        label_visibility="collapsed",
                        key=f"quiz_q_{i}"
                    )
                    if selected:
                        if selected == q["answer"]:
                            st.success(f"Correct! {q['explanation']}")
                        else:
                            st.error(
                                f"Not quite. Correct answer: "
                                f"**{q['answer']}**\n\n{q['explanation']}"
                            )
                    st.divider()

        # ── Flowchart ────────────────────────
        elif selected_tab == "🔀 Flowchart":
            mermaid_code = st.session_state["flowchart"]
            if not mermaid_code:
                st.info("No flowchart generated.")
            else:
                mermaid_html = f"""
                <div class="mermaid">
                {mermaid_code}
                </div>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js">
                </script>
                <script>
                    mermaid.initialize({{
                        startOnLoad: true,
                        theme: 'neutral',
                        flowchart: {{
                            curve: 'basis',
                            padding: 20
                        }}
                    }});
                </script>
                """
                st.components.v1.html(mermaid_html, height=600, scrolling=True)
                with st.expander("View Mermaid code"):
                    st.code(mermaid_code, language="text")

        # ── Ask a Question (RAG) ─────────────
        if st.session_state["rag_ready"]:
            st.divider()
            st.markdown("### 💬 Ask a Question")
            st.caption(
                "Ask anything about the video — "
                "answers are grounded in the transcript."
            )

            for entry in st.session_state["chat_history"]:
                with st.chat_message("user"):
                    st.write(entry["question"])
                with st.chat_message("assistant"):
                    st.write(entry["answer"])

            question = st.chat_input(
                "What would you like to know about this video?"
            )

            if question:
                with st.chat_message("user"):
                    st.write(question)
                with st.chat_message("assistant"):
                    with st.spinner("Searching transcript..."):
                        answer = answer_question(question)
                    st.write(answer)

                st.session_state["chat_history"].append({
                    "question": question,
                    "answer": answer
                })

        # ── PDF Export ───────────────────────
        st.divider()
        st.markdown("### 📥 Export")

        if st.button("Generate PDF", use_container_width=True):
            with st.spinner("Building PDF..."):
                pdf_bytes = generate_pdf(
                    url=st.session_state["url"] or "Audio Upload",
                    summary=st.session_state["summary"],
                    flashcards=st.session_state["flashcards"] or [],
                    quiz=st.session_state["quiz"] or []
                )
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name="knowledge_copilot.pdf",
                mime="application/pdf",
                use_container_width=True
            )


# ─────────────────────────────────────────────
# MEETING MODE
# ─────────────────────────────────────────────
elif mode == "💼 Meeting Mode":

    st.markdown("Paste your meeting transcript below.")

    transcript_input = st.text_area(
        "Meeting Transcript",
        placeholder="Paste your meeting transcript here...",
        height=200
    )

    generate_btn = st.button(
        "Generate MoM",
        type="primary",
        use_container_width=True
    )

    if generate_btn and transcript_input:
        st.session_state["mom"] = None
        try:
            with st.spinner("Processing transcript..."):
                chunks = chunk_text(transcript_input)
            with st.spinner("Generating Minutes of Meeting..."):
                from services.mom import generate_mom
                st.session_state["mom"] = generate_mom(chunks)
            st.success("Done!")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

    elif generate_btn and not transcript_input:
        st.warning("Please paste a meeting transcript first.")

    if st.session_state.get("mom"):
        st.divider()
        st.markdown(st.session_state["mom"])
        st.download_button(
            label="⬇️ Download MoM",
            data=st.session_state["mom"],
            file_name="minutes_of_meeting.txt",
            mime="text/plain"
        )