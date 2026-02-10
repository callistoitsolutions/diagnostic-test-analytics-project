import pandas as pd
from analytics.schema_mapper import map_columns
from database.db_connection import engine

def process_file(file_path):
    df = pd.read_excel(file_path)

    # Map Excel columns to standard schema
    df = map_columns(df)
    print("Columns after mapping:", df.columns.tolist())

    df.drop_duplicates(inplace=True)

    # Date handling
    if 'test_date' in df.columns:
        df['test_date'] = pd.to_datetime(df['test_date'], errors='coerce')

    # PRICE IS MANDATORY
    if 'test_price' not in df.columns:
        raise ValueError(
            "Price column not found. Please update schema_config.json"
        )

    # Revenue handling
    if 'revenue' not in df.columns:
        df['revenue'] = df['test_price']
    else:
        df['revenue'] = df['revenue'].fillna(df['test_price'])

    # ✅ KEEP ONLY COLUMNS THAT EXIST IN MYSQL TABLE
    allowed_columns = [
        'patient_id',
        'test_name',
        'test_category',
        'test_date',
        'test_price',
        'revenue'
    ]

    df = df[allowed_columns]

    # Insert into MySQL
    df.to_sql(
        "test_transactions",
        engine,
        if_exists="append",
        index=False
    )

    print("Data inserted successfully")
