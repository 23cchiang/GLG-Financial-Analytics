import sqlite3

# -----------------------------
# Connect to database
# -----------------------------

conn = sqlite3.connect("../database.db")
cursor = conn.cursor()

# -----------------------------
# Get historical revenue
# -----------------------------

cursor.execute("""
SELECT month, revenue
FROM monthly_financials
ORDER BY month
""")

rows = cursor.fetchall()

# -----------------------------
# Display historical data
# -----------------------------

print("\nHistorical Revenue")

for month, revenue in rows:
    print(f"{month}: ${revenue:,.2f}")

# -----------------------------
# Calculate growth rates
# -----------------------------

growth_rates = []

for i in range(1, len(rows)):

    previous_revenue = rows[i - 1][1]
    current_revenue = rows[i][1]

    growth = (current_revenue - previous_revenue) / previous_revenue

    growth_rates.append(growth)

# -----------------------------
# Average growth
# -----------------------------

avg_growth = sum(growth_rates) / len(growth_rates)

print(f"\nAverage Growth Rate: {avg_growth:.2%}")

# -----------------------------
# Forecast assumptions
# -----------------------------

SCENARIOS = {
    "Conservative": 0.05,
    "Expected": 0.10,
    "Aggressive": avg_growth
}

forecast_months = [
    "2026-05",
    "2026-06",
    "2026-07",
    "2026-08",
    "2026-09",
    "2026-10",
    "2026-11",
    "2026-12"
]

last_revenue = rows[-1][1]

# -----------------------------
# Generate forecasts
# -----------------------------

for scenario, growth in SCENARIOS.items():

    print("\n" + "=" * 50)
    print(f"{scenario} Forecast")
    print("=" * 50)

    current_revenue = last_revenue

    for month in forecast_months:

        current_revenue *= (1 + growth)

        print(
            f"{month}: ${current_revenue:,.2f}"
        )

# -----------------------------
# Close connection
# -----------------------------

conn.close()