
from pathlib import Path
from pypdf import PdfReader
import chromadb

# Project folder: D:\chatvocate\backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Change this to your actual PDF folder and filename.
PDF_PATH = BASE_DIR / "load_documents" / "IPC.pdf"

# ChromaDB stores its database files in this folder.
CHROMA_PATH = BASE_DIR / "chroma_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def split_text(text):
    """Split text into chunks with a small overlap."""
    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunks.append(text[start:end])

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def ingest_document():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF not found: {PDF_PATH}\n"
            "Check the folder name and PDF filename."
        )

    reader = PdfReader(str(PDF_PATH))

    client = chromadb.PersistentClient(
        path=str(CHROMA_PATH)
    )

    collection = client.get_or_create_collection(
        name="legal_documents"
    )

    ids = []
    documents = []
    metadatas = []

    document_name = PDF_PATH.name

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        chunks = split_text(page_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            # Stable IDs prevent duplicate entries on reruns.
            chunk_id = (
                f"{document_name}-page-{page_number}"
                f"-chunk-{chunk_number}"
            )

            ids.append(chunk_id)
            documents.append(chunk)

            metadatas.append({
                "source": document_name,
                "page": page_number,
                "chunk": chunk_number,
            })

    if not documents:
        print("No extractable text found in the PDF.")
        print("The PDF may require OCR.")
        return

    # Insert new chunks or update existing chunks with the same IDs.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print("Document ingestion completed!")
    print("PDF:", document_name)
    print("Total pages:", len(reader.pages))
    print("Total chunks:", len(documents))
    print("Chunks stored:", collection.count())
    print("ChromaDB location:", CHROMA_PATH)


if __name__ == "__main__":
    ingest_document()