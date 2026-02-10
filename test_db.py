from database.db_connection import engine

conn = engine.connect()
print("Database connected successfully")
conn.close()
