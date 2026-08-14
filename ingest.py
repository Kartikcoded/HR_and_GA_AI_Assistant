"""
ingest.py
Run whenever new HR/GA policy documents are added to data/raw/.
Safe to re-run — already-ingested chunks are skipped.
"""

from app.ingestion.loader import load_all_documents
from app.ingestion.chunker import chunk_all_documents
from app.retrieval.vectorstore import add_chunks

DATA_FOLDER = "data/raw"


def run_ingestion():
    docs = load_all_documents(DATA_FOLDER)
    print(f"Loaded {len(docs)} document(s).")
    chunks = chunk_all_documents(docs)
    print(f"Created {len(chunks)} chunk(s).")
    add_chunks(chunks)
    print("Ingestion complete.")


if __name__ == "__main__":
    run_ingestion()