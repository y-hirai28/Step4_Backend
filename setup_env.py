
import os

# Content with clean formatting (no leading spaces)
env_content = 'DATABASE_URL="mysql+pymysql://students:10th-tech0@gen10-mysql-dev-01.mysql.database.azure.com/vision_care_db"'

file_path = ".env"

try:
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    print(f"Successfully wrote to {file_path}")
except Exception as e:
    print(f"Error writing .env: {e}")
