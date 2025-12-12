
import os
import pymysql
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    print("Starting migration...")
    
    if not DATABASE_URL.startswith("mysql"):
        print("Not using MySQL. Skipping migration (SQLite handles altered models differently or needs manual recreation).")
        # For SQLite local dev (if used), usually we just delete the DB file or use alembic. 
        # But user is using Azure MySQL.
        return

    # Parse URL
    # mysql+pymysql://user:password@host:port/dbname
    url_str = DATABASE_URL.replace("mysql+pymysql://", "mysql://")
    url = urlparse(url_str)
    
    conn = pymysql.connect(
        host=url.hostname,
        user=url.username,
        password=url.password,
        database=url.path.lstrip('/'),
        port=url.port or 3306,
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"check_hostname": False, "verify_mode": False} # Same as app/database.py
    )
    
    try:
        with conn.cursor() as cursor:
            # Check if columns exist
            cursor.execute("SHOW COLUMNS FROM Child LIKE 'age'")
            if cursor.fetchone():
                print("Column 'age' already exists.")
            else:
                print("Adding column 'age'...")
                cursor.execute("ALTER TABLE Child ADD COLUMN age INT NULL")
                
            cursor.execute("SHOW COLUMNS FROM Child LIKE 'grade'")
            if cursor.fetchone():
                print("Column 'grade' already exists.")
            else:
                print("Adding column 'grade'...")
                cursor.execute("ALTER TABLE Child ADD COLUMN grade VARCHAR(20) NULL")
                
            conn.commit()
            print("Migration successful.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
