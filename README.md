
# 🧠 AI Knowledge Copilot

> Transform any YouTube video into structured, actionable learning materials — instantly.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ai-knowledge-copilot1.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/kirandeepkaur1bangar-art/AI-Knowledge-Copilot)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-Llama%204-FF6B35?style=for-the-badge)](https://groq.com)

---

## 🚀 Live Demo

**Try it now:** [https://ai-knowledge-copilot1.streamlit.app](https://ai-knowledge-copilot1.streamlit.app)

Paste any YouTube URL and get a full learning kit in under 30 seconds — no signup, no install.

---

## 📌 What It Does

Most people watch educational videos passively. This tool converts any YouTube video into a complete learning kit:

| Output | Description |
|---|---|
| 📄 **Summary** | Structured overview with key concepts and takeaways |
| 🃏 **Flashcards** | 8 spaced-repetition cards for active recall |
| ❓ **Quiz** | 5 multiple choice questions with explanations |
| 🔀 **Flowchart** | Visual concept map showing the story of the content |
| 💬 **Q&A** | Ask anything — answers grounded strictly in the transcript |
| 📥 **PDF Export** | Download everything as a clean PDF |

---

## 🏗️ Architecture

```
YouTube URL / Audio File
        ↓
  transcript.py        ← captions fetch (fast) or Whisper (fallback)
        ↓
  chunker.py           ← smart overlapping chunks (1500 chars, 200 overlap)
        ↓
  ┌─────────────────────────────────────┐
  │           AI Engine (Groq)          │
  │  summarizer.py  → structured summary│
  │  flashcards.py  → JSON flashcards   │
  │  quiz.py        → MCQ with answers  │
  │  flowchart.py   → Mermaid diagram   │
  └─────────────────────────────────────┘
        ↓
  rag.py               ← ChromaDB + sentence-transformers
        ↓
  pdf_export.py        ← ReportLab PDF generation
        ↓
  frontend/app.py      ← Streamlit UI
```

---

## ✨ Key Features

### 🎯 Smart Transcript Extraction
- Fetches YouTube captions instantly (manual + auto-generated)
- Supports non-English videos — Hindi, Spanish, French, and 97 more languages
- Whisper fallback for videos without captions (local, free)
- Audio file upload for meeting recordings and podcasts

### 🤖 RAG-Powered Q&A
- Embeds transcript chunks using `all-MiniLM-L6-v2` (distilled BERT encoder)
- Stores vectors in ChromaDB for semantic search
- Answers grounded strictly in transcript — no hallucination
- Ask in any language, get answers from the content

### 📊 Hierarchical Summarisation
- Short videos: 1 LLM call
- Long videos: batch → summarise → combine summaries
- Handles any length automatically

### 🔀 Narrative Flowchart
- Visual story map — not just a concept list
- Shows problem → argument → conclusion flow
- Rendered with Mermaid.js

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| LLM | Groq (Llama 4 Scout) | Free tier, fastest inference available |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Distilled BERT, runs locally, free |
| Vector Store | ChromaDB | Local vector DB, zero config |
| Transcription | youtube-transcript-api + Whisper | Caption-first, Whisper fallback |
| Text Splitting | LangChain RecursiveCharacterTextSplitter | Sentence-aware chunking |
| UI | Streamlit | Fast Python UI |
| PDF | ReportLab | Pure Python PDF generation |
| Deployment | Streamlit Cloud | Free hosting, auto-deploy from GitHub |

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

```bash
# Clone the repo
git clone https://github.com/kirandeepkaur1bangar-art/AI-Knowledge-Copilot.git
cd AI-Knowledge-Copilot

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "LLM_PROVIDER=groq" > .env
echo "GROQ_API_KEY=your_key_here" >> .env

# Run the app
streamlit run frontend/app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 📁 Project Structure

```
AI-Knowledge-Copilot/
│
├── services/
│   ├── llm.py              # Groq API wrapper — single place to control AI
│   ├── transcript.py       # YouTube URL → plain text (captions + Whisper)
│   ├── chunker.py          # Smart overlapping text chunking
│   ├── summarizer.py       # Hierarchical summarisation
│   ├── flashcards.py       # Structured JSON flashcard generation
│   ├── quiz.py             # Multiple choice quiz generation
│   ├── flowchart.py        # Mermaid.js concept map generation
│   ├── rag.py              # ChromaDB vector store + Q&A retrieval
│   └── pdf_export.py       # ReportLab PDF generation
│
├── prompts/                # All LLM prompt templates (versioned)
│   ├── summary.txt
│   ├── flashcards.txt
│   ├── quiz.txt
│   ├── flowchart.txt
│   └── rag.txt
│
├── frontend/
│   └── app.py              # Streamlit UI
│
├── .streamlit/
│   └── config.toml         # Streamlit theme config
│
├── requirements.txt
└── README.md
```

---

## 🧠 Engineering Concepts Used

This project demonstrates real engineering principles — not just API calls:

- **Abstraction** — `get_transcript()` hides caption vs Whisper complexity from callers
- **DRY principle** — `llm.py` as single source of truth for AI engine
- **Graceful fallback** — caption API → Whisper → clear error message
- **Prompt engineering** — structured JSON output for reliable parsing
- **RAG pipeline** — embed → store → retrieve → answer
- **Hierarchical processing** — summarise summaries for long content
- **Provider abstraction** — swap Groq for Claude in one line

---

## 🗺️ Roadmap

- [x] Phase 1 — YouTube → Summary, Flashcards, Quiz, Flowchart
- [x] Phase 2 — Flowchart generation with Mermaid.js
- [x] Phase 3 — RAG: Ask questions over transcript
- [x] Phase 4 — Audio file upload with Whisper
- [x] Phase 5 — PDF export
- [x] Phase 6 — Deploy to Streamlit Cloud
- [ ] Phase 7 — Multi-video memory (ask across multiple videos)
- [ ] Phase 8 — Meeting Mode (MoM, action items, decisions)
- [ ] Phase 9 — Browser extension

---

## 👩‍💻 Author

**Kirandeep Kaur**
[GitHub](https://github.com/kirandeepkaur1bangar-art)

---

## 📄 License

MIT License — feel free to use, modify, and build on this.
