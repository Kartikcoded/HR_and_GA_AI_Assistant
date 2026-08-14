"""
init_db.py
Run once to create all tables defined in app/db/models.py.
"""

from app.db.database import Base, engine
from app.db import models  # noqa: F401 — import registers the models with Base

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
