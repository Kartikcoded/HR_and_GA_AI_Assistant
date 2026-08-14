"""
nodes.py
Individual node functions for the LangGraph agent. Each node
receives the current AgentState, does one job, and returns the
fields it updated.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.agent.state import AgentState
load_dotenv()
from app.retrieval.vectorstore import query_collection
from app.integrations.servicenow.client import create_incident, ServiceNowError

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

INTENT_PROMPT = """Classify the employee's message into exactly one category:

- "knowledge_query": they're asking a question about a policy (leave, travel, IT assets, HR/GA rules).
- "action_request": they need something done — a ticket, request, or issue reported (laptop problem, access request, leave request, facility issue, complaint).

Respond with only the category name, nothing else.

Message: {question}"""


def classify_intent(state: AgentState) -> dict:
    """Node 1: decide whether this is a question or an action request."""
    prompt = INTENT_PROMPT.format(question=state["question"])
    response = llm.invoke(prompt)
    intent = response.content.strip()

    if intent not in ("knowledge_query", "action_request"):
        intent = "knowledge_query"  # safe default: prefer answering over guessing at an action

    return {"intent": intent}


def retrieve_knowledge(state: AgentState) -> dict:
    """Node 2a: retrieve relevant policy chunks (knowledge_query path)."""
    chunks = query_collection(state["question"], top_k=3)
    return {"retrieved_chunks": chunks}

def create_ticket(state: AgentState) -> dict:
    """
    Node: create a real ServiceNow ticket for the employee's request.
    Handles both explicit action requests and the knowledge-gap
    fallback path — either way, the employee's original question
    becomes the ticket description.
    """
    try:
        result = create_incident(
            short_description=state["question"][:160],  # ServiceNow field length limit
            description=state["question"],
            urgency="3",
        )
        ticket_number = result["number"]
        answer = f"I've created a ticket for this: {ticket_number}. The relevant team will follow up."
        return {"ticket_number": ticket_number, "answer": answer}

    except ServiceNowError as e:
        # Never let the employee believe a ticket was created when it wasn't.
        answer = (
            "I wasn't able to create a ticket automatically due to a system issue. "
            "Please contact HR/GA support directly, or try again shortly."
        )
        return {"ticket_number": None, "answer": answer}

def generate_answer(state: AgentState) -> dict:
    """Node 3a: generate a grounded answer, or flag if context is insufficient."""
    context = "\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in state["retrieved_chunks"]
    )
    prompt = f"""Answer the employee's HR/GA question using ONLY this context.

If the context does NOT contain enough information to answer, respond with \
EXACTLY this text and nothing else: NO_INFO_FOUND

Context:
{context}

Question: {state['question']}

Answer:"""
    response = llm.invoke(prompt)
    print("LLM response:", response)
    return {"answer": response.content.strip()}
