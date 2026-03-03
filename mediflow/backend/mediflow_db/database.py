# ================================================================
#  mediflow_db/database.py  — COMPATIBILITY SHIM (do not delete)
#  Everything re-exported from config.py so nothing breaks.
# ================================================================

from mediflow_db.config import Base, engine, SessionLocal, get_db, test_connection

__all__ = ["Base", "engine", "SessionLocal", "get_db", "test_connection"]
