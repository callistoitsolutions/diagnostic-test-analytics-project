import pandas as pd
from database.db_connection import engine

def load_data():
    query = """
        SELECT
            patient_id,
            test_name,
            test_category,
            test_date,
            test_price,
            revenue
        FROM test_transactions
    """
    return pd.read_sql(query, engine)
