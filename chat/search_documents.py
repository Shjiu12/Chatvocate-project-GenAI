
from pathlib import Path
import chromadb


# Locate the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Connect to the existing ChromaDB database
CHROMA_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

# Open the same collection used during ingestion
collection = client.get_or_create_collection(
    name="legal_documents"
)


def search_legal_documents(question, number_of_results=3):
    """
    Search the stored legal document for relevant passages.
    """

    if not question or not question.strip():
        return []

    total_chunks = collection.count()

    if total_chunks == 0:
        return []

    results = collection.query(
        query_texts=[question.strip()],
        n_results=min(number_of_results, total_chunks)
    )

    matches = []

    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    distances = results.get("distances") or [[]]

    for document, metadata, distance in zip(
        documents[0],
        metadatas[0],
        distances[0]
    ):
        matches.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "page": metadata.get("page"),
            "distance": distance,
        })

    return matches


if __name__ == "__main__":
    question = input("Enter your legal question: ")

    matches = search_legal_documents(question)

    if not matches:
        print("No matching passages found.")
    else:
        for index, match in enumerate(matches, start=1):
            print(f"\n--- Result {index} ---")
            print("Source:", match["source"])
            # print("Page:", match["page"])
            print("Text:", match["text"])
            print("Distance:", match["distance"])