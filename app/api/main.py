"""
main.py
FastAPI backend: authenticated endpoint that runs employee questions
through the LangGraph agent and logs the interaction to PostgreSQL.
"""

from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import get_db
from app.db.crud import log_conversation, log_ticket
from app.auth.dependencies import get_current_user
from app.api.auth_routes import router as auth_router
from app.agent.graph import agent

app = FastAPI(
    title="Enterprise HR & GA AI Assistant",
    description="RAG + agentic assistant for HR/GA policy Q&A and ServiceNow ticket automation",
    version="1.0.0",
)

app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    ticket_number: str | None = None


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=AnswerResponse)
def ask(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Log the incoming question before processing — so we have a
    # record even if something downstream fails.
    log_conversation(db, current_user["user_id"], "user", request.question)

    result = agent.invoke({"question": request.question})
    answer = result.get("answer", "I wasn't able to process that request.")
    ticket_number = result.get("ticket_number")

    log_conversation(db, current_user["user_id"], "assistant", answer)

    if ticket_number:
        log_ticket(
            db,
            user_id=current_user["user_id"],
            ticket_type=result.get("intent", "unknown"),
            description=request.question,
            servicenow_ticket_number=ticket_number,
            status="created",
        )

    return AnswerResponse(answer=answer, ticket_number=ticket_number)