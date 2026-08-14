"""
database.py
Sets up the SQLAlchemy engine and session factory for PostgreSQL.
Other modules import `SessionLocal` to get a database session,
and `Base` to define models against.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# The engine manages the actual connection pool to Postgres.
engine = create_engine(DATABASE_URL)

# Each request gets its own Session — SQLAlchemy's unit-of-work
# object for tracking changes before committing them to the DB.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All model classes will inherit from this Base, which is how
# SQLAlchemy knows which Python classes map to database tables.
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI: yields a DB session per request
    and guarantees it's closed afterward, even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()