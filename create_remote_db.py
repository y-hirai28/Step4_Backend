
import pymysql
import ssl
import os

# Connection Details
HOST = "gen10-mysql-dev-01.mysql.database.azure.com"
USER = "students"
PASSWORD = "10th-tech0"
DB_NAME = "vision_care_db"

def create_db():
    print(f"Attempting to connect to {HOST}...")
    
    # Configure SSL Context (Accept self-signed / skip verification for dev)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        # Connect without DB specified
        conn = pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            port=3306,
            ssl=ctx,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        print(f"Connected. Creating database '{DB_NAME}' if it doesn't exist...")
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
        print("Database creation command executed.")
        
        # Verify
        cursor.execute("SHOW DATABASES;")
        dbs = [row[0] for row in cursor.fetchall()]
        print("Existing databases:", dbs)
        
        if DB_NAME in dbs:
            print(f"SUCCESS: Database '{DB_NAME}' exists.")
        else:
            print(f"WARNING: Database '{DB_NAME}' not found in list.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to create database. Reason: {e}")

if __name__ == "__main__":
    create_db()
