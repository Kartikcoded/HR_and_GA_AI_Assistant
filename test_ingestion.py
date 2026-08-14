from app.ingestion.loader import load_all_documents
from app.ingestion.chunker import chunk_all_documents

docs = load_all_documents("data/raw")
chunks = chunk_all_documents(docs)

print(f"Documents loaded: {len(docs)}")
print(f"Chunks created: {len(chunks)}")
print("\n--- Sample chunk ---")
print(chunks[0]["chunk_id"])
print(chunks[0]["text"][:300])