# Hotel Booking Analytics Dashboard

Interactive dashboard built with Python, Pandas, Plotly and Streamlit.

**Note:** this is a self-practice portfolio project, not paid client work. The data is the public
"Hotel Booking Demand" dataset (Kaggle), cleaned with Pandas. Please check the dataset license and cite the source.

## What it shows
- 5 KPI cards: bookings, cancellation rate, average daily rate, average stay, revenue (canceled stays excluded)
- Auto-written key insights that follow the filters
- Monthly bookings with cancellation rate, cancellation by hotel, market segments, customer types,
  top countries, average daily rate by month, cancellation by booking lead time
- Sidebar filters: hotel, year, market segment, customer type
- Filtered data table with CSV download
- Responsive layout (laptop, tablet, phone); charts do not move when touched on a phone

## Data cleaning (119,390 rows to 119,209)
- Removed private columns (name, email, phone number, credit card) and the mostly empty `company` column
- Filled blank `children` with 0, blank `country` with "Unknown", blank `agent` with 0
- Removed 1 row with negative price and 180 rows with zero guests
- Added: total nights, total guests, arrival year-month

## Run locally
```
pip install -r requirements.txt
streamlit run app.py
```
