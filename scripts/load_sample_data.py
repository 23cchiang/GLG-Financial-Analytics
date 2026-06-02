import sqlite3

data = [
    ("2026-01", 27630.24, 9603.51, 9527.26, 5042.00, 451.17, 92.31, 2913.99),
    ("2026-02", 33166.70, 12155.55, 9899.92, 5042.00, 479.41, 326.86, 5262.96),
    ("2026-03", 41965.82, 13371.63, 12485.90, 5042.00, 193.99, 505.64, 10366.66),
    ("2026-04", 48516.47, 12625.88, 21778.32, 5042.00, 32.40, 363.81, 8674.06)
]

conn = sqlite3.connect("../database.db")
cursor = conn.cursor()

cursor.executemany("""
INSERT INTO monthly_financials
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", data)

conn.commit()
conn.close()

print("Data insterted")