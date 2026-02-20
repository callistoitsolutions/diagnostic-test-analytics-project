from sqlalchemy import create_engine
from urllib.parse import quote_plus

# Railway MySQL credentials
DB_USER = "root"
DB_PASSWORD = quote_plus("uUMEFBuCNTEndAyOShcXwaiuPTeLYZda")
DB_HOST = "mysql.railway.internal"
DB_PORT = "3306"
DB_NAME = "railway"

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

print("✅ Database engine created successfully")