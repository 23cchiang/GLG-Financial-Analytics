import sqlite3

conn = sqlite3.connect("../database.db")

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM monthly_financials
ORDER BY month
""")

rows = cursor.fetchall()

for row in rows:

    month = row[0]
    revenue = row[1]
    payroll = row[2]
    supplies = row[3]
    rent = row[4]
    software = row[5]
    marketing = row[6]
    profit = row[7]

    payroll_pct = payroll / revenue * 100
    supplies_pct = supplies / revenue * 100
    rent_pct = rent / revenue * 100
    net_margin = profit / revenue * 100

    print(f"\n{month}")
    print(f"Revenue: ${revenue:,.2f}")
    print(f"Net Margin: {net_margin:.2f}%")
    print(f"Payroll %: {payroll_pct:.2f}%")
    print(f"Supplies %: {supplies_pct:.2f}%")
    print(f"Rent %: {rent_pct:.2f}%")

conn.close()