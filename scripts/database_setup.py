import sqlite3

conn = sqlite3.connect('../database.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS monthly_financials (
    month TEXT,
    revenue REAL,
    payroll REAL,
    supplies REAL,
    rent REAL,
    software REAL,
    marketing REAL,
    profit REAL
)
""")

conn.commit()
conn.close()

print("Database created successfully")