"""
graph.py
Builds the LangGraph agent: classify intent, then route to the
appropriate path. Currently only the knowledge_query path is
fully wired; action_request routes to a placeholder.
"""

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import classify_intent, retrieve_knowledge, generate_answer
from app.agent.nodes import classify_intent, retrieve_knowledge, generate_answer, create_ticket

def route_by_intent(state: AgentState) -> str:
    """Conditional edge: decides which path to take after classification."""
    if state["intent"] == "knowledge_query":
        return "retrieve_knowledge"
    return "action_placeholder"


def action_placeholder(state: AgentState) -> dict:
    """Temporary stand-in until Steps 7-8 build the real ticket-creation path."""
    return {"answer": "Ticket creation isn't implemented yet — coming in a later step."}

def route_after_answer(state: AgentState) -> str:
    """
    Conditional edge after generate_answer: if the LLM couldn't find
    an answer in the retrieved context, escalate to ticket creation
    instead of leaving the employee with a dead end.
    """
    if state.get("answer") == "NO_INFO_FOUND":
        return "action_placeholder"
    return "end"

def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_knowledge", retrieve_knowledge)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("create_ticket", create_ticket)

    graph.set_entry_point("classify_intent")
    graph.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {"retrieve_knowledge": "retrieve_knowledge", "action_placeholder": "create_ticket"},
    )
    graph.add_edge("retrieve_knowledge", "generate_answer")
    graph.add_conditional_edges(
        "generate_answer",
        route_after_answer,
        {"action_placeholder": "create_ticket", "end": END},
    )
    graph.add_edge("create_ticket", END)

    return graph.compile()


agent = build_agent_graph()





