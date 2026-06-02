import sqlite3

import os

print(os.path.abspath("../database.db"))

conn = sqlite3.connect("../database.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM monthly_financials")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()