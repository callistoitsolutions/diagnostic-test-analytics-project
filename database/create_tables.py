import sys
import os
from sqlalchemy import text
from database.db_connection import engine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

with engine.connect() as conn:
    conn.execute(text("""
    CREATE TABLE IF NOT EXISTS test_transactions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id VARCHAR(50),
        test_name VARCHAR(255),
        test_category VARCHAR(255),
        test_price FLOAT,
        revenue FLOAT,
        test_date DATE
    )
    """))

print("✅ Table 'test_transactions' created successfully in TiDB")
