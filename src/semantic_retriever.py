
"""
CyberSentinel AI
Semantic Cybersecurity Knowledge Retriever

Uses local sentence embeddings and cosine similarity
to retrieve relevant cybersecurity knowledge.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

from src.knowledge_retriever import split_knowledge_into_sections


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None
_documents = None
_document_embeddings = None


def initialize_retriever():
    global _model, _documents, _document_embeddings

    if _model is not None:
        return

    print("Loading semantic embedding model...")

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu"
    )

    documents = split_knowledge_into_sections()

    if not documents:
        raise ValueError(
            "No cybersecurity knowledge sections were found."
        )

    document_texts = [
        document["content"]
        for document in documents
    ]

    embeddings = model.encode(
        document_texts,
        normalize_embeddings=True
    )

    _model = model
    _documents = documents
    _document_embeddings = embeddings

    print(
        f"Semantic retriever ready: {len(documents)} sections indexed."
    )


def retrieve_semantic_knowledge(query, top_k=3):
    initialize_retriever()

    if not query.strip() or top_k <= 0:
        return []

    query_embedding = _model.encode(
        [query],
        normalize_embeddings=True
    )[0]

    similarity_scores = (
        _document_embeddings @ query_embedding
    )

    ranked_indices = np.argsort(
        similarity_scores
    )[::-1]

    results = []

    for index in ranked_indices[:top_k]:
        document = _documents[int(index)]

        results.append({
            "title": document["title"],
            "content": document["content"],
            "source": document["source"],
            "similarity_score": round(
                float(similarity_scores[index]),
                4
            )
        })

    return results


if __name__ == "__main__":
    query = (
        "A computer is accessing many unfamiliar "
        "machines using multiple user accounts"
    )

    print("\nQuery:", query)

    results = retrieve_semantic_knowledge(
        query,
        top_k=3
    )

    print("\nRetrieved knowledge:")

    for result in results:
        print(
            f"- {result['title']} "
            f"| similarity: {result['similarity_score']}"
        )
