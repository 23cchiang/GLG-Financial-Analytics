import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime, date


def import_quickbooks(file_path):

    print(f"\nImporting: {file_path}")

    # ----------------------------
    # Read QuickBooks Export
    # ----------------------------

    df = pd.read_excel(
        file_path,
        header=3
    )

    # ----------------------------
    # Get Month Headers
    # ----------------------------

    raw_months = df.iloc[0, 1:].tolist()

    months_clean = []
    valid_column_indexes = []

    for idx, month in enumerate(raw_months):

        try:

            cleaned = datetime.strptime(
                str(month),
                "%b %Y"
            ).strftime("%Y-%m")

            months_clean.append(cleaned)

            valid_column_indexes.append(idx + 1)

        except ValueError:

            print(f"Skipping partial month: {month}")

    print("\nMonths Found:")
    print(months_clean)

    # ----------------------------
    # Helper Function
    # ----------------------------

    def get_row(label):

        row = df[df.iloc[:, 0] == label]

        if len(row) == 0:
            print(f"Could not find: {label}")
            return None

        values = []

        for col_idx in valid_column_indexes:

            values.append(row.iloc[0, col_idx])

        return values

    # ----------------------------
    # Extract Categories
    # ----------------------------

    revenue = get_row("Total for Income")
    payroll = get_row("Total for Payroll expenses")
    supplies = get_row("Supplies & Materials")
    rent = get_row("Building & property rent")
    marketing = get_row("Total for Advertising & marketing")
    profit = get_row("Net Operating Income")

    custom_software = get_row("Custom software or app")
    computer_software = get_row("Computer Software")
    software_apps = get_row("Software & apps")

    # ----------------------------
    # Combine Software Categories
    # ----------------------------

    software = []

    for i in range(len(months_clean)):

        total = 0

        if custom_software is not None:
            total += float(custom_software[i])

        if computer_software is not None:
            total += float(computer_software[i])

        if software_apps is not None:
            total += float(software_apps[i])

        software.append(round(total, 2))

    # ----------------------------
    # Database Connection
    # ----------------------------

    BASE_DIR = Path(__file__).resolve().parent.parent

    db_path = BASE_DIR / "database.db"

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # ----------------------------
    # Insert Data
    # ----------------------------

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
            Path(file_path).name,
            str(date.today())
        ))

    conn.commit()
    conn.close()

    print("\nQuickBooks import complete!")

    return True