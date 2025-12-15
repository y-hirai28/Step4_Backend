from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Build connection URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")

if DATABASE_URL:
    # Use explicit DATABASE_URL (e.g. from Azure)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
    
    connect_args = {}
    # Azure MySQL typically requires SSL
    if "azure.com" in SQLALCHEMY_DATABASE_URL:
        connect_args["ssl"] = {
             "ca": SSL_CERT_PATH,
             "check_hostname": False,
             "verify_mode": False
        }

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args
    )

elif DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    # Legacy/Individual vars
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    connect_args = {}
    if SSL_CERT_PATH and os.path.exists(SSL_CERT_PATH):
         connect_args["ssl"] = {
             "ca": SSL_CERT_PATH,
             "check_hostname": False,
             "verify_mode": False
         }

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=connect_args
    )
else:
    # Fallback to local SQLite
    SQLALCHEMY_DATABASE_URL = "sqlite:///./merelax.db"
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
