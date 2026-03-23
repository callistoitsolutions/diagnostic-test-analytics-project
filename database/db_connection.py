from sqlalchemy import create_engine
import streamlit as st

DATABASE_URL = st.secrets.get("TIDB_DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("TIDB_DATABASE_URL is not set in Streamlit Secrets")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280
)

print("✅ TiDB connected successfully")
