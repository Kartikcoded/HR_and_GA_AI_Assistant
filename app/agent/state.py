"""
state.py
Defines the shared state object that flows through every node
in the LangGraph agent. Every node reads from and writes to this
same state dict.
"""

from typing import TypedDict, Literal, Optional


class AgentState(TypedDict):
    question: str
    intent: Optional[Literal["knowledge_query", "action_request"]]
    retrieved_chunks: Optional[list[dict]]
    answer: Optional[str]
    ticket_number: Optional[str]