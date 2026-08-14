from app.retrieval.vectorstore import query_collection
from app.agent.nodes import generate_answer

question = "What is the policy for overtime?"

chunks = query_collection(question, top_k=3)
print("--- Retrieved chunks ---")
for c in chunks:
    print(f"[{c['distance']:.4f}] {c['text'][:150]}")
print()

state = {"question": question, "retrieved_chunks": chunks}
result = generate_answer(state)
print("--- LLM answer ---")
print(result["answer"])