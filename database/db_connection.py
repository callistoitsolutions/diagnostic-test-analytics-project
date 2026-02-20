from sqlalchemy import create_engine
import os

# Railway PUBLIC MySQL URL (required for Streamlit Cloud)
DATABASE_URL = os.getenv(
    "MYSQL_PUBLIC_URL",
    "mysql://root:uUMEFBuCNTEndAyOShcXwaiuPTeLYZda@crossover.proxy.rlwy.net:44781/railway"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

print("✅ Database engine created successfully")
