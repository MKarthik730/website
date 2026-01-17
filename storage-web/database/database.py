from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Update with your PostgreSQL credentials
db_url = "postgresql://postgres:password@localhost:5432/storage_web"
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
