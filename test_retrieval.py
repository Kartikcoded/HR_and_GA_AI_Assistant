
from app.retrieval.vectorstore import query_collection

results = query_collection("How many casual leave days am I entitled to?", top_k=3)

for r in results:
    print(f"[{r['distance']:.4f}] {r['source']}")
    print(r["text"][:200])
    print()