import pandas as pd
import sqlite3
from datetime import date

# --------------------------------------------------
# LOAD QUICKBOOKS FILE
# --------------------------------------------------

file_path = "../imports/Great Lakes Gaming, LLC_Profit and Loss.xlsx"

df = pd.read_excel(
    file_path,
    header=3
)

# --------------------------------------------------
# GET MONTHS
# (Ignoring partial June column)
# --------------------------------------------------

months = df.iloc[0, 1:6].tolist()

months_clean = [
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05"
]

# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def get_row(label):

    row = df[df.iloc[:, 0] == label]

    if len(row) == 0:
        print(f"Could not find: {label}")
        return None

    return row.iloc[0, 1:6].tolist()

# --------------------------------------------------
# EXTRACT FINANCIAL DATA
# --------------------------------------------------

revenue = get_row("Total for Income")

payroll = get_row("Total for Payroll expenses")

supplies = get_row("Supplies & Materials")

rent = get_row("Building & property rent")

marketing = get_row("Total for Advertising & marketing")

profit = get_row("Net Operating Income")

# --------------------------------------------------
# SOFTWARE CATEGORIES
# --------------------------------------------------

custom_software = get_row("Custom software or app")

computer_software = get_row("Computer Software")

software_apps = get_row("Software & apps")

software = []

for i in range(len(months)):

    total = 0

    if custom_software is not None:
        total += float(custom_software[i])

    if computer_software is not None:
        total += float(computer_software[i])

    if software_apps is not None:
        total += float(software_apps[i])

    software.append(round(total, 2))

# --------------------------------------------------
# DISPLAY EXTRACTED DATA
# --------------------------------------------------

print("\nRevenue")
print(revenue)

print("\nPayroll")
print(payroll)

print("\nSupplies")
print(supplies)

print("\nRent")
print(rent)

print("\nMarketing")
print(marketing)

print("\nSoftware")
print(software)

print("\nProfit")
print(profit)

# --------------------------------------------------
# CONNECT TO DATABASE
# --------------------------------------------------

conn = sqlite3.connect("../database.db")

cursor = conn.cursor()

# --------------------------------------------------
# INSERT DATA
# --------------------------------------------------

for i in range(len(months_clean)):

    cursor.execute("""
    INSERT OR REPLACE INTO monthly_financials
    (
        month,
        revenue,
        payroll,
        supplies,
        rent,
        software,
        marketing,
        profit,
        source_file,
        date_imported
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        months_clean[i],
        round(float(revenue[i]), 2),
        round(float(payroll[i]), 2),
        round(float(supplies[i]), 2),
        0 if pd.isna(rent[i]) else round(float(rent[i]), 2),
        round(float(software[i]), 2),
        round(float(marketing[i]), 2),
        round(float(profit[i]), 2),
        "QuickBooks_PnL.xlsx",
        str(date.today())
    ))

# --------------------------------------------------
# SAVE CHANGES
# --------------------------------------------------

conn.commit()
conn.close()

print("\nQuickBooks import complete!")