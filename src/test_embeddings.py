
"""
CyberSentinel AI
Local Embedding Model Test

Tests whether a sentence-transformer model
can generate semantic embeddings.
"""

from sentence_transformers import SentenceTransformer


def main():
    print("Loading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        device="cpu"
    )

    sentences = [
        "Unusual authentication activity across computers",
        "Potential lateral movement in a network",
        "A recipe for making chocolate cake"
    ]

    print("Generating embeddings...")

    embeddings = model.encode(
        sentences,
        normalize_embeddings=True
    )

    print("\nEmbedding model loaded successfully!")
    print("Number of sentences:", len(sentences))
    print("Embedding dimensions:", embeddings.shape[1])

    similarity = embeddings @ embeddings.T

    print("\nSemantic similarity scores:")
    print(
        "Authentication vs lateral movement:",
        round(float(similarity[0, 1]), 4)
    )
    print(
        "Authentication vs chocolate cake:",
        round(float(similarity[0, 2]), 4)
    )


if __name__ == "__main__":
    main()
