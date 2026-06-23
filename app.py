import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px

from scripts.import_functions import import_quickbooks
from sklearn.linear_model import LinearRegression
from scripts.supabase_client import supabase
GLG_PURPLE = "#800080"

# Create database if it doesn't exist

st.markdown("""
<style>
h1, h2, h3 {
    color: #800080;
}
</style>
""", unsafe_allow_html=True)

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

st.markdown("""
<style>
h1, h2, h3 {
    color: #800080;
}
</style>
""", unsafe_allow_html=True)

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
# BUDGET VS ACTUAL
# --------------------------------------------------

st.header("💰 Budget vs Actual")

budget_response = (
    supabase
    .table("budgets")
    .select("*")
    .execute()
)

budget_df = pd.DataFrame(
    budget_response.data
)

latest = df.iloc[-1]

# --------------------------------------------------
# EXECUTIVE KPI DASHBOARD
# --------------------------------------------------

revenue = float(latest["revenue"])

expenses = (
    float(latest["payroll"]) +
    float(latest["supplies"]) +
    float(latest["rent"]) +
    float(latest["software"]) +
    float(latest["marketing"])
)

profit = float(latest["profit"])

profit_margin = (
    (profit / revenue) * 100
    if revenue > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Revenue",
        f"${revenue:,.2f}"
    )

with col2:
    st.metric(
        "Expenses",
        f"${expenses:,.2f}"
    )

with col3:
    st.metric(
        "Profit",
        f"${profit:,.2f}"
    )

with col4:
    st.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%"
    )

st.divider()


comparison = pd.DataFrame({
    "Category": [
        "Payroll",
        "Marketing",
        "Software",
        "Rent"
    ],
    "Budget": [
        budget_df.loc[
            budget_df["category"] == "Payroll",
            "budget_amount"
        ].iloc[0],

        budget_df.loc[
            budget_df["category"] == "Marketing",
            "budget_amount"
        ].iloc[0],

        budget_df.loc[
            budget_df["category"] == "Software",
            "budget_amount"
        ].iloc[0],

        budget_df.loc[
            budget_df["category"] == "Rent",
            "budget_amount"
        ].iloc[0]
    ],

    "Actual": [
        latest["payroll"],
        latest["marketing"],
        latest["software"],
        latest["rent"]
    ]
})

comparison["Variance"] = (
    comparison["Actual"]
    - comparison["Budget"]
)

comparison["Status"] = comparison["Variance"].apply(
    lambda x: "🔴 Over Budget"
    if x > 0
    else "🟢 Under Budget"
)

comparison["Variance %"] = (
    comparison["Variance"]
    / comparison["Budget"]
    * 100
)

styled_comparison = (
    comparison.style
    .format({
        "Budget": "${:,.2f}",
        "Actual": "${:,.2f}",
        "Variance": "${:,.2f}",
        "Variance %": "{:.1f}%"
    })
    .map(
        lambda v:
        "color: red; font-weight: bold"
        if v > 0
        else "color: #800080; font-weight: bold",
        subset=["Variance"]
    )
)

st.dataframe(
    styled_comparison,
    use_container_width=True
)

st.subheader("Budget Summary")

over_budget = comparison[
    comparison["Variance"] > 0
]["Variance"].sum()

under_budget = abs(
    comparison[
        comparison["Variance"] < 0
    ]["Variance"].sum()
)

st.subheader("Recommendations")

for _, row in comparison.iterrows():

    if row["Variance"] > 0:

        st.warning(
            f"{row['Category']} exceeds budget by "
            f"${row['Variance']:,.2f}"
        )

    elif row["Variance"] < 0:

        st.success(
            f"{row['Category']} is under budget by "
            f"${abs(row['Variance']):,.2f}"
        )

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "🔴 Over Budget",
        f"${over_budget:,.2f}"
    )


with col2:
    st.metric(
        "🟢 Under Budget",
        f"${under_budget:,.2f}"
    )

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

st.header("Operational KPIs")

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

st.header("Revenue Trend")

fig = px.line(
    df,
    x="month",
    y="revenue",
    title="Revenue Trend"
)

fig.update_traces(
    line_color="#800080",
    line_width=4
)

st.plotly_chart(
    fig,
    use_container_width=True
)

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

fig = px.bar(
    expense_df,
    x="Category",
    y="Amount",
    color_discrete_sequence=["#800080"],
    text="Amount"
)

fig.update_traces(
    texttemplate="$%{y:,.0f}",
    textposition="outside"
)

st.plotly_chart(
    fig,
    use_container_width=True
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

import plotly.express as px

fig = px.line(
    chart_df,
    y=[
        "Historical Revenue",
        "Growth Forecast",
        "Regression Forecast"
    ]
)

fig.update_traces(
    line=dict(width=4)
)

fig.data[0].line.color = "#800080"
fig.data[1].line.color = "#9932CC"
fig.data[2].line.color = "#BA55D3"

fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    legend_title_text=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)

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

forecast_display = forecast_table.copy()

forecast_display["Growth Forecast"] = (
    forecast_display["Growth Forecast"]
    .map(lambda x: f"${x:,.0f}")
)

forecast_display["Regression Forecast"] = (
    forecast_display["Regression Forecast"]
    .map(lambda x: f"${x:,.0f}")
)


st.dataframe(
    forecast_display,
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
    display_df = df.copy()

    money_columns = [
        "revenue",
        "payroll",
        "supplies",
        "rent",
        "software",
        "marketing",
        "profit"
    ]

    for col in money_columns:
        display_df[col] = display_df[col].map(
            lambda x: f"${x:,.2f}"
        )

    st.dataframe(
        display_df,
        use_container_width=True
    )