"""
Run this once to create the database tables:
    python init_db.py
"""
from db import Base, engine
import models 

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")