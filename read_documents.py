
from pypdf import PdfReader

pdf_path = "load_documents/IPC.pdf"

reader = PdfReader(pdf_path)

print("Total pages:", len(reader.pages))

full_text = []

for page_number, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""

    if text.strip():
        full_text.append({
            "page": page_number,
            "text": text
        })

print("Pages containing extractable text:", len(full_text))

print("\nFirst page preview:\n")
if full_text:
    print(full_text[0]["text"][:2000])
else:
    print("No extractable text found.")