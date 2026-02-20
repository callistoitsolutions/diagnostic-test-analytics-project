import pandas as pd
from database.db_connection import engine

df = pd.read_excel("data.xlsx")  # your Excel file

df.to_sql(
    name="test_transactions",
    con=engine,
    if_exists="append",
    index=False
)

print("✅ Excel data inserted into Railway MySQL")