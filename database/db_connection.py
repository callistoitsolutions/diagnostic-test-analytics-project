from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in Streamlit Secrets")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

print("✅ Railway MySQL connected successfully")
