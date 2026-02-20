from db import engine

try:
    with engine.connect() as conn:
        print("✅ Connected to Railway MySQL successfully")
except Exception as e:
    print("❌ Connection failed:", e)
