# ================================================================
#  mediflow_db/config.py  — SINGLE SOURCE OF TRUTH for DB setup
# ================================================================

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

db_url = os.getenv("DB_URL")
if not db_url:
    raise RuntimeError("DB_URL is not set in your .env file")

engine = create_engine(
    db_url,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ PostgreSQL connected")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        raise
