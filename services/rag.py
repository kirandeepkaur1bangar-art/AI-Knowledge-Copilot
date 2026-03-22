# services/rag.py

import os
import chromadb
from sentence_transformers import SentenceTransformer
from llm import ask_llm

# ─────────────────────────────────────────────
# Load embedding model once at module level
# Why here? Loading takes ~2 seconds.
# If we loaded inside a function, it would reload
# on every question. Loading once = fast queries.
# ─────────────────────────────────────────────
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedding model ready.")

# ChromaDB client — stores vectors in memory
# In Phase 5 we'll persist to disk
client = chromadb.Client()


def build_index(chunks: list[str], collection_name: str = "transcript") -> None:
    """
    Takes transcript chunks and stores them in ChromaDB
    as embeddings. Called once after transcript is fetched.

    Parameters:
        chunks: list of text chunks from chunker.py
        collection_name: name for this transcript's collection
    """

    # Delete existing collection if it exists
    # So switching videos starts fresh
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    # Create fresh collection
    collection = client.create_collection(collection_name)

    print(f"  Building index for {len(chunks)} chunks...")

    # Convert all chunks to embeddings in one batch
    # Batch processing is faster than one by one
    embeddings = embedder.encode(chunks).tolist()

    # Store in ChromaDB
    # Each chunk needs a unique ID
    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

    print(f"  Index built. {len(chunks)} chunks stored.")


def retrieve(question: str, collection_name: str = "transcript", top_k: int = 3) -> list[str]:
    """
    Finds the most relevant chunks for a question.

    Parameters:
        question: user's question
        collection_name: which transcript to search
        top_k: how many chunks to retrieve

    Returns:
        list of the most relevant text chunks
    """

    collection = client.get_collection(collection_name)

    # Convert question to embedding
    question_embedding = embedder.encode([question]).tolist()

    # Find closest chunks by cosine similarity
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=top_k
    )

    # results["documents"] is a list of lists — flatten it
    return results["documents"][0]


def answer_question(question: str, collection_name: str = "transcript") -> str:
    """
    Full RAG pipeline — retrieve relevant chunks then answer.

    Parameters:
        question: user's question
        collection_name: which transcript to search

    Returns:
        grounded answer string
    """

    # Step 1: retrieve relevant chunks
    relevant_chunks = retrieve(question, collection_name)

    # Step 2: build context string
    context = "\n\n---\n\n".join(relevant_chunks)

    # Step 3: build prompt — strictly grounded in context
    prompt = f"""You are a helpful assistant answering questions about a video transcript.

Answer the question using ONLY the context provided below.
If the answer is not in the context, say "I couldn't find that in the transcript."
Do not use any outside knowledge.

Context from transcript:
{context}

Question: {question}

Answer:"""

    return ask_llm(prompt)


