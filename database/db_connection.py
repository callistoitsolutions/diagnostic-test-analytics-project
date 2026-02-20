from sqlalchemy import create_engine
from urllib.parse import quote_plus

DB_USER = "MYSQL_USER_FROM_RAILWAY"
DB_PASSWORD = quote_plus("MYSQL_PASSWORD_FROM_RAILWAY")
DB_HOST = "MYSQL_HOST_FROM_RAILWAY"
DB_PORT = "MYSQL_PORT_FROM_RAILWAY"
DB_NAME = "MYSQL_DATABASE_FROM_RAILWAY"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("✅ Database engine created successfully")
