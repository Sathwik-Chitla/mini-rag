from pathlib import Path
from typing import List, Dict
import numpy as np
import faiss
import requests
from sentence_transformers import SentenceTransformer


DATA_DIR = Path("data")


def load_documents() -> List[Dict]:
    chunks = []

    for path in DATA_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        sections = content.split("\n\n")

        for idx, section in enumerate(sections):
            section = section.strip()
            if len(section) < 100:
                continue

            chunks.append({
                "text": section,
                "source": path.name,
                "id": f"{path.stem}_{idx}"
            })

    return chunks


def embed_chunks(chunks: List[Dict]):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [c["text"] for c in chunks]

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return vectors, model


def build_index(vectors: np.ndarray):
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def retrieve(query: str, model, index, chunks: List[Dict], k: int = 3):
    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(query_vector, k)

    results = []
    for i, score in zip(indices[0], scores[0]):
        results.append({
            "score": float(score),
            "chunk": chunks[i]
        })

    return results


def ask_ollama(query: str, retrieved: List[Dict]) -> str:
    context = "\n\n".join(item["chunk"]["text"] for item in retrieved)

    prompt = f"""
You are an AI assistant for Indecimal.

Answer the question using ONLY the information provided below.
If the answer is not present, say:
"I do not have enough information in the provided documents."

Context:
{context}

Question:
{query}

Answer:
""".strip()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2}
        }
    )

    return response.json()["response"]


if __name__ == "__main__":
    documents = load_documents()
    embeddings, embedder = embed_chunks(documents)
    index = build_index(embeddings)

    queries = [
        "How does Indecimal handle construction delays?",
        "How are customer payments protected during construction?",
        "What is Indecimal’s quality assurance system?",
        "How many quality checkpoints are followed?",
        "Does Indecimal provide real-time project tracking?",
        "What does stage-based contractor payment mean?",
        "What post-construction maintenance support is offered?",
        "How does Indecimal reduce hidden surprises in pricing?",
        "What construction packages does Indecimal offer?",
        "What does a wallet amount mean in package specifications?",
        "What is Indecimal’s refund policy after project cancellation?"
    ]

    for query in queries:
        print(f"\nQUERY: {query}\n")
        print("Retrieved Context:\n")

        retrieved = retrieve(query, embedder, index, documents, k=3)

        for i, item in enumerate(retrieved, 1):
            print(
                f"[{i}] Source: {item['chunk']['source']} | "
                f"Score: {item['score']:.4f}"
            )
            print(item["chunk"]["text"][:500].strip())
            print()

        answer = ask_ollama(query, retrieved)

        print("Final Answer:\n")
        print(answer.strip())
        print("\n" + "-" * 80)
