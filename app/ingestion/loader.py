"""
loader.py
Extracts raw text from PDF and DOCX HR/GA policy documents.
Returns a consistent structure regardless of source format.
"""

from pathlib import Path
from pypdf import PdfReader
from docx import Document as DocxDocument


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def load_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def load_document(file_path: str) -> dict:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        text = load_pdf(file_path)
    elif suffix == ".docx":
        text = load_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    return {"source": path.name, "text": text}


def load_all_documents(folder_path: str) -> list[dict]:
    folder = Path(folder_path)
    documents = []
    for file_path in folder.iterdir():
        if file_path.suffix.lower() in [".pdf", ".docx"]:
            try:
                documents.append(load_document(str(file_path)))
            except Exception as e:
                print(f"Skipping {file_path.name}: {e}")
    return documents

