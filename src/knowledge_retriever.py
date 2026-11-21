
"""
CyberSentinel AI
Local Cybersecurity Knowledge Retriever

Initial version: Keyword-based retrieval.
Future version: Embedding-based semantic search.
"""

from pathlib import Path
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent

KNOWLEDGE_FILE = (
    PROJECT_ROOT
    / "knowledge"
    / "authentication_threats.md"
)


def load_knowledge():
    if not KNOWLEDGE_FILE.exists():
        raise FileNotFoundError(
            f"Knowledge file not found: {KNOWLEDGE_FILE}"
        )

    return KNOWLEDGE_FILE.read_text(
        encoding="utf-8"
    )


def split_knowledge_into_sections():
    text = load_knowledge()

    sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

    documents = []

    for section in sections:
        section = section.strip()

        if not section.startswith("## "):
            continue

        lines = section.splitlines()

        title = lines[0].replace("## ", "", 1).strip()

        documents.append({
            "title": title,
            "content": section,
            "source": "knowledge/authentication_threats.md"
        })

    return documents


def retrieve_knowledge(query, top_k=3):
    documents = split_knowledge_into_sections()

    query_words = set(
        re.findall(r"[a-zA-Z]+", query.lower())
    )

    results = []

    for document in documents:
        document_words = set(
            re.findall(
                r"[a-zA-Z]+",
                document["content"].lower()
            )
        )

        score = len(query_words.intersection(document_words))

        if score > 0:
            results.append({
                **document,
                "relevance_score": score
            })

    results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    return results[:top_k]
