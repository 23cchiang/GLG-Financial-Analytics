import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression

conn = sqlite3.connect("../database.db")

df = pd.read_sql_query(
    """
    SELECT month, revenue
    FROM monthly_financials
    ORDER BY month
    """,
    conn
)

conn.close()

# Convert months to numbers
df["month_num"] = range(len(df))

X = df[["month_num"]]
y = df["revenue"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Forecast next 6 months
future_months = pd.DataFrame({
    "month_num": range(
        len(df),
        len(df) + 6
    )
})

forecast = model.predict(future_months)

print("\nForecasted Revenue:\n")

for value in forecast:
    print(f"${value:,.2f}")