from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
db_url="postgresql://postgres:karthik988%2c%2c@localhost:5432/karthik"
engine =create_engine(db_url)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)