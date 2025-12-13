from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Build connection URL from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME")
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH")

if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    # Azure MySQL
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    connect_args = {}
    if SSL_CERT_PATH:
         connect_args["ssl"] = {
             "ca": SSL_CERT_PATH,
             "check_hostname": False, # Adjust as needed for dev/prod
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

# .envファイルから環境変数を読み込む
load_dotenv()

# データベース接続URLの構築
# DATABASE_URLが直接指定されている場合はそれを使用
# それ以外の場合は個別の環境変数から構築
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 個別の環境変数から構築
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")

    if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
        # MySQL接続URLを構築
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    else:
        # デフォルトはSQLite
        DATABASE_URL = "sqlite:///./merelax.db"

SQLALCHEMY_DATABASE_URL = DATABASE_URL

# データベース接続エンジンの設定
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLiteの場合、check_same_thread用の接続引数が必要
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # Azure MySQL 接続設定（SSL設定含む）
    ssl_cert_path = os.getenv("SSL_CERT_PATH")

    if ssl_cert_path:
        # SSL証明書を使用する場合
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={
                "ssl": {
                    "ca": ssl_cert_path
                }
            },
            pool_pre_ping=True,  # 接続の有効性を確認
            pool_recycle=3600    # 1時間ごとに接続をリサイクル
        )
    else:
        # SSL証明書なし（検証スキップ）
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={
                "ssl": {
                    "check_hostname": False,
                    "verify_mode": False
                }
            },
            pool_pre_ping=True,
            pool_recycle=3600
        )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
