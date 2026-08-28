"""Seed the configured database with labelled, deterministic NER-LENS demo data."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401
from app.services.demo_data import seed_demo_data

Base.metadata.create_all(bind=engine)
with SessionLocal() as session:
    seed_demo_data(session)
print("NER-LENS demo data is ready.")
