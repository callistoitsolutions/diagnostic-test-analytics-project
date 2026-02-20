from sqlalchemy import create_engine
from urllib.parse import quote_plus

DB_USER = "root"
DB_PASSWORD = quote_plus("uUMEFBuCNTEndAyOShcXwaiuPTeLYZda")
DB_HOST = "crossover.proxy.rlwy.net"
DB_PORT = "44781"
DB_NAME = "railway"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("✅ Database engine created successfully")
