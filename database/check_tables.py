from sqlalchemy import text
from database.db_connection import engine

with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES"))
    print("📋 Tables in database:")
    for row in result:
        print(row)