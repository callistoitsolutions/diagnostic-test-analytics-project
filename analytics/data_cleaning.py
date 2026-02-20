import pandas as pd
from analytics.schema_mapper import map_columns
from database.db_connection import engine

def process_file(file_path):
    df = pd.read_excel(file_path)

    # Map Excel columns to standard schema
    df = map_columns(df)
    print("Columns after mapping:", df.columns.tolist())

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # ---------- DATE CLEANING ----------
    if 'test_date' in df.columns:
        df['test_date'] = pd.to_datetime(
            df['test_date'],
            errors='coerce'
        )

    # ---------- PRICE (MANDATORY) ----------
    if 'test_price' not in df.columns:
        raise ValueError(
            "Price column not found. Please update schema_config.json"
        )

    # Clean test_price
    df['test_price'] = (
        df['test_price']
        .astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    df['test_price'] = pd.to_numeric(
        df['test_price'],
        errors='coerce'
    )

    # ---------- REVENUE ----------
    if 'revenue' not in df.columns:
        df['revenue'] = df['test_price']
    else:
        df['revenue'] = (
            df['revenue']
            .astype(str)
            .str.replace("₹", "", regex=False)
            .str.replace(",", "", regex=False)
        )
        df['revenue'] = pd.to_numeric(
            df['revenue'],
            errors='coerce'
        )
        df['revenue'] = df['revenue'].fillna(df['test_price'])

    # ---------- KEEP ONLY MYSQL COLUMNS ----------
    allowed_columns = [
        'patient_id',
        'test_name',
        'test_category',
        'test_date',
        'test_price',
        'revenue'
    ]
    df = df[allowed_columns]

    # ---------- NaN → NULL (CRITICAL) ----------
    df = df.where(pd.notnull(df), None)

    # ---------- INSERT INTO MYSQL ----------
    df.to_sql(
        "test_transactions",
        engine,
        if_exists="append",
        index=False,
        method="multi"   # VERY IMPORTANT
    )

    print("✅ Data inserted successfully")
