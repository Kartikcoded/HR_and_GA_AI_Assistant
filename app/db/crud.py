"""
crud.py
Simple database write helpers for logging conversations and tickets.
"""

from sqlalchemy.orm import Session
from app.db.models import Conversation, Ticket


def log_conversation(db: Session, user_id: int, role: str, message: str):
    entry = Conversation(user_id=user_id, role=role, message=message)
    db.add(entry)
    db.commit()


def log_ticket(db: Session, user_id: int, ticket_type: str, description: str,
                servicenow_ticket_number: str | None, status: str):
    entry = Ticket(
        user_id=user_id,
        ticket_type=ticket_type,
        description=description,
        servicenow_ticket_number=servicenow_ticket_number,
        status=status,
    )
    db.add(entry)
    db.commit()
    