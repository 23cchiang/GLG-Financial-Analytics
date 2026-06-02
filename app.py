import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# Page Setup
# --------------------------------------------------

st.set_page_config(
    page_title="GLG Financial Analytics",
    layout="wide"
)

st.title("GLG Financial Analytics Dashboard")

# --------------------------------------------------
# Scenario Selector
# --------------------------------------------------

scenario = st.selectbox(
    "Forecast Scenario",
    ["Conservative", "Expected", "Aggressive"]
)

# --------------------------------------------------
# Load Database Data
# --------------------------------------------------

conn = sqlite3.connect("database.db")

actual_df = pd.read_sql_query(
    """
    SELECT *
    FROM monthly_financials
    ORDER BY month
    """,
    conn
)

forecast_df = pd.read_sql_query(
    """
    SELECT *
    FROM forecasts
    ORDER BY month
    """,
    conn
)

conn.close()

selected_forecast = forecast_df[
    forecast_df["scenario"] == scenario
]

# --------------------------------------------------
# Latest KPIs
# --------------------------------------------------

latest = actual_df.iloc[-1]

revenue = latest["revenue"]
payroll = latest["payroll"]
supplies = latest["supplies"]
rent = latest["rent"]
software = latest["software"]
marketing = latest["marketing"]
profit = latest["profit"]

net_margin = profit / revenue * 100
payroll_pct = payroll / revenue * 100
supplies_pct = supplies / revenue * 100

# --------------------------------------------------
# KPI Cards
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"${revenue:,.0f}"
    )

with col2:
    st.metric(
        "Net Margin",
        f"{net_margin:.2f}%"
    )

with col3:
    st.metric(
        "Payroll %",
        f"{payroll_pct:.2f}%"
    )

with col4:
    st.metric(
        "Supplies %",
        f"{supplies_pct:.2f}%"
    )

st.divider()

# --------------------------------------------------
# Revenue Trend
# --------------------------------------------------

st.subheader("Revenue Trend")

st.line_chart(
    actual_df.set_index("month")["revenue"]
)

st.divider()

# --------------------------------------------------
# Expense Composition
# --------------------------------------------------

st.subheader("Expense Composition")

expense_df = pd.DataFrame({
    "Category": [
        "Payroll",
        "Supplies",
        "Rent",
        "Software",
        "Marketing"
    ],
    "Amount": [
        payroll,
        supplies,
        rent,
        software,
        marketing
    ]
})

expense_fig = px.pie(
    expense_df,
    values="Amount",
    names="Category",
    hole=0.4,
    title=f"Expense Breakdown ({latest['month']})"
)

st.plotly_chart(
    expense_fig,
    use_container_width=True
)

st.divider()

# --------------------------------------------------
# Actual vs Forecast Revenue
# --------------------------------------------------

st.subheader("Actual vs Forecast Revenue")

forecast_fig = go.Figure()

forecast_fig.add_trace(
    go.Scatter(
        x=actual_df["month"],
        y=actual_df["revenue"],
        mode="lines+markers",
        name="Actual Revenue"
    )
)

forecast_fig.add_trace(
    go.Scatter(
        x=selected_forecast["month"],
        y=selected_forecast["revenue"],
        mode="lines+markers",
        name=f"{scenario} Forecast"
    )
)

forecast_fig.update_layout(
    title=f"{scenario} Revenue Forecast",
    xaxis_title="Month",
    yaxis_title="Revenue ($)",
    height=500
)

st.plotly_chart(
    forecast_fig,
    use_container_width=True
)

# --------------------------------------------------
# Forecast Summary
# --------------------------------------------------

if not selected_forecast.empty:

    december_forecast = selected_forecast.iloc[-1]["revenue"]

    st.subheader("Forecast Summary")

    st.metric(
        "Projected December Revenue",
        f"${december_forecast:,.0f}"
    )

# --------------------------------------------------
# Raw Data
# --------------------------------------------------

with st.expander("View Historical Financial Data"):
    st.dataframe(actual_df)

with st.expander("View Forecast Data"):
    st.dataframe(selected_forecast)