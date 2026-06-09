import streamlit as st
import pandas as pd
import sqlite3
import os
from scripts.import_functions import import_quickbooks

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
# DATABASE CONNECTION
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

# --------------------------------------------------
# CHECK DATA EXISTS
# --------------------------------------------------

if len(df) == 0:

    st.warning("No financial data found.")

    conn.close()

    st.stop()

# --------------------------------------------------
# LATEST MONTH
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
# KPI CARDS
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
# REVENUE TREND
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

expense_data = pd.DataFrame(
    {
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
    }
)

st.bar_chart(
    expense_data.set_index("Category")
)

# --------------------------------------------------
# SIMPLE FORECAST
# --------------------------------------------------

st.divider()

st.header("Revenue Forecast")

growth_rates = []

revenues = df["revenue"].tolist()

for i in range(1, len(revenues)):

    growth = (
        revenues[i] - revenues[i - 1]
    ) / revenues[i - 1]

    growth_rates.append(growth)

avg_growth = (
    sum(growth_rates)
    / len(growth_rates)
)

future_revenue = revenues[-1]

forecast_months = []
forecast_values = []

for i in range(6):

    future_revenue *= (1 + avg_growth)

    forecast_months.append(
        f"Forecast {i+1}"
    )

    forecast_values.append(
        round(future_revenue, 2)
    )

forecast_df = pd.DataFrame(
    {
        "Month": forecast_months,
        "Revenue": forecast_values
    }
)

st.line_chart(
    forecast_df.set_index("Month")
)

st.metric(
    "Projected Revenue (6 Months)",
    f"${forecast_values[-1]:,.0f}"
)

# --------------------------------------------------
# IMPORT INFO
# --------------------------------------------------

st.divider()

st.header("Import Information")

st.write(
    f"Last Source File: "
    f"{latest['source_file']}"
)

st.write(
    f"Last Import Date: "
    f"{latest['date_imported']}"
)

# --------------------------------------------------
# HISTORICAL DATA
# --------------------------------------------------

with st.expander(
    "View Historical Financial Data"
):
    st.dataframe(df)

# --------------------------------------------------
# CLOSE CONNECTION
# --------------------------------------------------

conn.close()