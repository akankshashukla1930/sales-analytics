# Sales Analytics Pipeline (SQL + Python + Excel)

Synthetic retail sales data → SQLite → Python analysis (window functions, joins) →
auto-generated Excel dashboard with charts. No server/DB install needed.

## Files
- `generate_data.py` — creates `data/sales_data.csv` (8000 synthetic orders, 300 customers)
- `schema.sql` — DDL: `customers`, `orders` tables + indexes
- `load_data.py` — loads CSV into `sales.db` (SQLite file)
- `analysis.py` — SQL queries (monthly revenue, top products, regional margin,
  churn/recency, RFM segmentation via `NTILE()`)
- `generate_report.py` — builds `sales_report.xlsx` (5 sheets, charts) from analysis.py
- `sales.db` — generated SQLite database
- `sales_report.xlsx` — final deliverable

## How to run (in order)
```bash
python3 generate_data.py     # step 1: create synthetic CSV
python3 load_data.py         # step 2: build sales.db from schema.sql + CSV
python3 analysis.py          # step 3 (optional): print query results to console
python3 generate_report.py   # step 4: build sales_report.xlsx
```

## What's happening
1. **generate_data.py** fakes a realistic sales CSV — customers, regions, products,
   dates, sales/profit — so the project is self-contained (no Kaggle download needed).
2. **load_data.py** runs `schema.sql` against a fresh `sales.db`, then uses
   `pandas.to_sql()` to bulk-insert the CSV into normalized `customers`/`orders` tables.
3. **analysis.py** is the SQL layer — each function is one query: monthly trend
   (`GROUP BY strftime`), top products (`GROUP BY` + `ORDER BY`), regional margin (`JOIN`),
   churn signal (`julianday()` date math), and RFM segments (`NTILE(4) OVER (...)` — a
   window function, no Python-side ranking).
4. **generate_report.py** pulls each query result into a pandas DataFrame, writes it to
   its own sheet in `sales_report.xlsx` with `openpyxl`, and attaches a matching chart
   (line for trend, bar for products/regions, pie for category share).

## Output sheets
`Dashboard` (KPIs + 2 charts) · `Top Products` (bar chart) · `Churn Risk`
(customers inactive 180+ days) · `RFM Segments` · `Category Trend` (pivot + pie chart)

## Re-running with your own data
Replace `data/sales_data.csv` with real data using the same columns, skip
`generate_data.py`, and run steps 2–4.
