"""
vectorstore.py
Wraps ChromaDB: stores HR/GA policy chunk embeddings persistently
and provides similarity search. Designed to be called as a tool
by the LangGraph agent added in a later step.
"""

import chromadb
from app.retrieval.embedder import embed_texts

CHROMA_PATH = "vectorstore"
COLLECTION_NAME = "hr_ga_policies"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)


def add_chunks(chunks: list[dict]):
    """Embed and store chunks, skipping any already-ingested chunk_ids."""
    collection = get_collection()
    existing_ids = set(collection.get()["ids"])

    new_chunks = [c for c in chunks if c["chunk_id"] not in existing_ids]
    if not new_chunks:
        print("No new chunks to add — all already ingested.")
        return

    texts = [c["text"] for c in new_chunks]
    embeddings = embed_texts(texts)
    ids = [c["chunk_id"] for c in new_chunks]
    metadatas = [{"source": c["source"]} for c in new_chunks]

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    print(f"Added {len(new_chunks)} new chunks (skipped {len(chunks) - len(new_chunks)} already-existing).")


def query_collection(query_text: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve the top_k most relevant HR/GA policy chunks for a query.
    This function is the retrieval 'tool' the agent will call when
    it classifies a question as a knowledge lookup rather than an action.
    """
    collection = get_collection()
    query_embedding = embed_texts([query_text])[0]

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    output = []
    for i in range(len(results["ids"][0])):
        output.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "distance": results["distances"][0][i],
        })
    return output

# def query_collection(query_text: str, top_k: int = 3, threshold: float = 0.7):
#     collection = get_collection()
#     query_embedding = embed_texts([query_text])[0]

#     results = collection.query(
#         query_embeddings=[query_embedding],
#         n_results=top_k,
#     )

#     output = []

#     for i in range(len(results["ids"][0])):
#         distance = results["distances"][0][i]
#         similarity = 1 - distance

#         if similarity >= threshold:
#             output.append({
#                 "chunk_id": results["ids"][0][i],
#                 "text": results["documents"][0][i],
#                 "source": results["metadatas"][0][i]["source"],
#                 "distance": distance,
#                 "similarity": similarity,
#             })

#     return output