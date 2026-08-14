"""
models.py
SQLAlchemy models defining the database schema:
users, conversations (chat history), and tickets (local log of
ServiceNow tickets created by the assistant).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    role = Column(String, nullable=False, default="employee")  # used for RBAC
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)   # "user" or "assistant"
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="conversations")


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    servicenow_ticket_number = Column(String, nullable=True)  # filled in after creation
    ticket_type = Column(String, nullable=False)  # e.g. "laptop_issue", "leave_request"
    description = Column(Text, nullable=False)
    status = Column(String, default="pending")     # pending, created, failed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="tickets")