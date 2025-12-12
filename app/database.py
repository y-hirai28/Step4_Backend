# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use environment variable for production (Azure MySQL), fallback to SQLite for local
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./merelax.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
# For SQLite, we might need connect_args specific for check_same_thread
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Azure MySQL connection arguments
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={
            "ssl": {
                "check_hostname": False,
                "verify_mode": False  # Assuming we can skip verification for dev, or just rely on system context
            }
        }
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
