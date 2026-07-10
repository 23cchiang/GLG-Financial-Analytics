# GLG-Financial-Analytics

A financial analytics and forecasting platform built using Python, SQLite, and Streamlit. This application automates KPI reporting, revenue forecasting, expense analysis, and financial dashboard generation from QuickBooks exports.

## Features

### KPI Dashboard

* Revenue tracking
* Net margin analysis
* Payroll percentage monitoring
* Supplies percentage monitoring

### Revenue Forecasting

* Conservative growth scenario
* Expected growth scenario
* Aggressive growth scenario
* Interactive forecast visualization

### Financial Analysis

* Revenue trend analysis
* Expense composition breakdown
* Historical financial data storage
* Forecast summary metrics

### Database Integration

* SQLite-backed data storage
* Historical financial record management
* Forecast data persistence

## Project Structure

```text
GLG-Financial-Analytics/

├── data/
├── imports/
├── reports/
├── scripts/
│   ├── database_setup.py
│   ├── load_sample_data.py
│   ├── view_data.py
│   ├── kpis.py
│   └── forecast.py
│
├── app.py
├── database.db
├── requirements.txt
└── README.md
```

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd GLG-Financial-Analytics
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Dashboard

Launch the Streamlit application:

```bash
streamlit run app.py
```

The dashboard will be available locally at:

```text
https://glg-financial.streamlit.app/
```

## Current Functionality

* Stores financial data in SQLite
* Calculates key business KPIs
* Generates revenue forecasts
* Supports multiple forecast scenarios
* Displays interactive financial dashboards

## Planned Features

* QuickBooks import automation
* Actual vs. forecast variance analysis
* Executive summary generation
* Automated PDF reporting
* Vendor analytics
* Multi-year financial tracking

## Technologies Used

* Python
* SQLite
* Streamlit
* Pandas
* Plotly

## Author

Chloe Chiang

Applied Mathematics Student | Financial Analytics | Data Analysis | Python Development
