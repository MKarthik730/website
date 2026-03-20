# ================================================================
#  mediflow_db/init_db.py
# ================================================================

from sqlalchemy import text
from mediflow_db.config import engine, Base, test_connection

# CRITICAL: importing models registers all ORM classes onto Base
import mediflow_db.models  # noqa: F401 — DO NOT REMOVE

SCHEMAS = ["organization", "users", "scheduling", "queue", "analytics"]


def create_schemas():
    with engine.begin() as conn:
        for schema in SCHEMAS:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
            print(f"  ✔ Schema '{schema}' ready")


def create_tables(drop_existing=False):
    table_count = len(Base.metadata.tables)
    print(f"  Registered tables: {table_count}")
    if table_count == 0:
        raise RuntimeError(
            "No tables registered on Base! "
            "Make sure models.py imports Base from mediflow_db.config"
        )

    if drop_existing:
        print("  ⚠ Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
    print("  ✔ Tables created")


def init_db(drop_existing=False):
    print("\nInitialising DB...\n")
    test_connection()
    create_schemas()
    create_tables(drop_existing)
    print("\n✅ DB fully initialised\n")


if __name__ == "__main__":
    init_db(drop_existing=True)
