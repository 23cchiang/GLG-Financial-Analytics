import streamlit as st
import pandas as pd
import sqlite3
import os

from scripts.import_functions import import_quickbooks
from sklearn.linear_model import LinearRegression

# Create database if it doesn't exist

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS monthly_financials (
    month TEXT PRIMARY KEY,
    revenue REAL,
    payroll REAL,
    supplies REAL,
    rent REAL,
    software REAL,
    marketing REAL,
    profit REAL,
    source_file TEXT,
    date_imported TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS forecasts (
    month TEXT,
    scenario TEXT,
    revenue REAL
)
""")

conn.commit()
conn.close()
# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="GLG Financial Analytics Dashboard",
    layout="wide"
)

st.title("GLG Financial Analytics Dashboard")

# --------------------------------------------------
# QUICKBOOKS UPLOAD
# --------------------------------------------------

st.header("Upload QuickBooks Report")

uploaded_file = st.file_uploader(
    "Choose a QuickBooks Profit & Loss Export",
    type=["xlsx"]
)

if uploaded_file is not None:

    os.makedirs("imports", exist_ok=True)

    save_path = os.path.join(
        "imports",
        uploaded_file.name
    )

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Import QuickBooks Data"):

        import_quickbooks(save_path)

        st.success("QuickBooks Import Complete!")

        st.rerun()


# --------------------------------------------------
# PASSWORD PROTECTION
# --------------------------------------------------
from config import DASHBOARD_PASSWORD

password = st.text_input(
    "Enter Dashboard Password",
    type="password"
)

if password == "":
    st.stop()

if password != st.secrets["dashboard_password"]:
    st.error("Incorrect password.")
    st.stop()

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

conn = sqlite3.connect("database.db")

df = pd.read_sql_query(
    """
    SELECT *
    FROM monthly_financials
    ORDER BY month
    """,
    conn
)

conn.close()

# --------------------------------------------------
# CHECK FOR DATA
# --------------------------------------------------

if len(df) == 0:

    st.warning("No financial data found.")

    st.stop()

# --------------------------------------------------
# LATEST MONTH KPIs
# --------------------------------------------------

latest = df.iloc[-1]

revenue = latest["revenue"]
profit = latest["profit"]

net_margin = (
    profit / revenue * 100
    if revenue != 0
    else 0
)

payroll_pct = (
    latest["payroll"] / revenue * 100
    if revenue != 0
    else 0
)

supplies_pct = (
    latest["supplies"] / revenue * 100
    if revenue != 0
    else 0
)

# --------------------------------------------------
# KPI DASHBOARD
# --------------------------------------------------

st.header("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Revenue",
    f"${revenue:,.0f}"
)

col2.metric(
    "Net Margin",
    f"{net_margin:.2f}%"
)

col3.metric(
    "Payroll %",
    f"{payroll_pct:.2f}%"
)

col4.metric(
    "Supplies %",
    f"{supplies_pct:.2f}%"
)

# --------------------------------------------------
# HISTORICAL REVENUE
# --------------------------------------------------

st.divider()

st.header("Revenue Trend")

revenue_chart = df[["month", "revenue"]].copy()

revenue_chart = revenue_chart.set_index("month")

st.line_chart(revenue_chart)

# --------------------------------------------------
# EXPENSE BREAKDOWN
# --------------------------------------------------

st.divider()

st.header("Expense Breakdown")

expense_df = pd.DataFrame({
    "Category": [
        "Payroll",
        "Supplies",
        "Rent",
        "Software",
        "Marketing"
    ],
    "Amount": [
        latest["payroll"],
        latest["supplies"],
        latest["rent"],
        latest["software"],
        latest["marketing"]
    ]
})

st.bar_chart(
    expense_df.set_index("Category")
)

# --------------------------------------------------
# GROWTH FORECAST
# --------------------------------------------------

revenues = df["revenue"].tolist()

growth_rates = []

for i in range(1, len(revenues)):

    growth = (
        revenues[i] - revenues[i - 1]
    ) / revenues[i - 1]

    growth_rates.append(growth)

avg_growth = sum(growth_rates) / len(growth_rates)

growth_forecast = []

future_revenue = revenues[-1]

for i in range(6):

    future_revenue *= (1 + avg_growth)

    growth_forecast.append(
        round(future_revenue, 2)
    )

# --------------------------------------------------
# REGRESSION FORECAST
# --------------------------------------------------

reg_df = df.copy()

reg_df["month_num"] = range(len(reg_df))

X = reg_df[["month_num"]]

y = reg_df["revenue"]

model = LinearRegression()

model.fit(X, y)

future_X = pd.DataFrame({
    "month_num": range(
        len(reg_df),
        len(reg_df) + 6
    )
})

regression_forecast = model.predict(
    future_X
)

regression_forecast = [
    round(x, 2)
    for x in regression_forecast
]

# --------------------------------------------------
# FORECAST COMPARISON
# --------------------------------------------------

st.divider()

st.header("Forecast Comparison")

col1, col2 = st.columns(2)

col1.metric(
    "Growth Model",
    f"${growth_forecast[-1]:,.0f}"
)

col2.metric(
    "Regression Model",
    f"${regression_forecast[-1]:,.0f}"
)

# --------------------------------------------------
# COMBINED FORECAST CHART
# --------------------------------------------------

historical = df["revenue"].tolist()

chart_df = pd.DataFrame({
    "Historical Revenue":
        historical + [None] * 6,

    "Growth Forecast":
        [None] * len(historical)
        + growth_forecast,

    "Regression Forecast":
        [None] * len(historical)
        + regression_forecast
})

st.subheader(
    "Historical vs Forecasted Revenue"
)

st.line_chart(chart_df)

# --------------------------------------------------
# FORECAST TABLE
# --------------------------------------------------

forecast_table = pd.DataFrame({
    "Month Ahead": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6"
    ],
    "Growth Forecast":
        growth_forecast,

    "Regression Forecast":
        regression_forecast
})

st.dataframe(
    forecast_table,
    use_container_width=True
)

# --------------------------------------------------
# IMPORT INFORMATION
# --------------------------------------------------

st.divider()

st.header("Import Information")

st.write(
    f"Source File: {latest['source_file']}"
)

st.write(
    f"Date Imported: {latest['date_imported']}"
)

# --------------------------------------------------
# HISTORICAL DATA
# --------------------------------------------------

with st.expander(
    "View Historical Financial Data"
):

    st.dataframe(
        df,
        use_container_width=True
    )