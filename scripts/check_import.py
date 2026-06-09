import sqlite3

# Connect to database
conn = sqlite3.connect("../database.db")

cursor = conn.cursor()

# Get all imported records
cursor.execute("""
SELECT *
FROM monthly_financials
ORDER BY month
""")

rows = cursor.fetchall()

print("\nMONTHLY FINANCIALS TABLE\n")

for row in rows:
    print(row)

conn.close()

print("\nDatabase check complete!")