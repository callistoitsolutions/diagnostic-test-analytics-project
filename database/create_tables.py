
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


import pandas as pd
from database.db_connection import engine  # ✅ FIXED

df = pd.DataFrame({
    "patient_id": [],
    "test_name": [],
    "test_category": [],
    "test_price": [],
    "test_date": [],
    "revenue": []
})

df.to_sql(
    name="test_transactions",
    con=engine,
    if_exists="replace",
    index=False
)

print("✅ Table 'test_transactions' created in Railway MySQL")