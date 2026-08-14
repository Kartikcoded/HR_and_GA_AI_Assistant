from app.retrieval.vectorstore import query_collection

results = query_collection("How many casual leave days do I get per year?", top_k=3)

for r in results:
    print(f"[distance: {r['distance']:.4f}] source: {r['source']}")
    print(r["text"])
    print("---")