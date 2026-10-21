"""
Runs analytical SQL queries against sales.db and returns pandas DataFrames.
Used standalone (prints results) and imported by generate_report.py.
"""
import sqlite3
import pandas as pd

DB_PATH = "sales.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def monthly_revenue(conn):
    return pd.read_sql_query("""
        SELECT strftime('%Y-%m', order_date) AS month,
               ROUND(SUM(sales), 2) AS total_sales,
               ROUND(SUM(profit), 2) AS total_profit
        FROM orders
        GROUP BY month
        ORDER BY month;
    """, conn)


def top_products(conn, limit=10):
    return pd.read_sql_query(f"""
        SELECT product_name, category,
               SUM(quantity) AS units_sold,
               ROUND(SUM(sales), 2) AS total_sales,
               ROUND(SUM(profit), 2) AS total_profit
        FROM orders
        GROUP BY product_name, category
        ORDER BY total_profit DESC
        LIMIT {limit};
    """, conn)


def regional_performance(conn):
    return pd.read_sql_query("""
        SELECT c.region,
               COUNT(DISTINCT o.order_id) AS num_orders,
               ROUND(SUM(o.sales), 2) AS total_sales,
               ROUND(SUM(o.profit), 2) AS total_profit,
               ROUND(SUM(o.profit) / SUM(o.sales) * 100, 2) AS margin_pct
        FROM orders o
        JOIN customers c ON c.customer_id = o.customer_id
        GROUP BY c.region
        ORDER BY total_sales DESC;
    """, conn)


def customer_recency(conn):
    """Days since each customer's last order — churn-risk signal."""
    return pd.read_sql_query("""
        SELECT c.customer_id, c.customer_name, c.region,
               MAX(o.order_date) AS last_order_date,
               CAST(julianday('2025-09-01') - julianday(MAX(o.order_date)) AS INTEGER) AS days_inactive,
               COUNT(o.order_id) AS total_orders,
               ROUND(SUM(o.sales), 2) AS lifetime_sales
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY days_inactive DESC;
    """, conn)


def customer_rfm_segments(conn):
    """RFM-lite segmentation using window function NTILE."""
    return pd.read_sql_query("""
        WITH recency AS (
            SELECT customer_id,
                   CAST(julianday('2025-09-01') - julianday(MAX(order_date)) AS INTEGER) AS days_inactive,
                   COUNT(order_id) AS frequency,
                   SUM(sales) AS monetary
            FROM orders
            GROUP BY customer_id
        )
        SELECT customer_id, days_inactive, frequency, ROUND(monetary, 2) AS monetary,
               NTILE(4) OVER (ORDER BY days_inactive ASC)  AS recency_quartile,
               NTILE(4) OVER (ORDER BY frequency DESC)     AS frequency_quartile,
               NTILE(4) OVER (ORDER BY monetary DESC)      AS monetary_quartile
        FROM recency
        ORDER BY monetary DESC;
    """, conn)


def category_month_trend(conn):
    """Category sales by month — pivoted later in Excel."""
    return pd.read_sql_query("""
        SELECT strftime('%Y-%m', order_date) AS month,
               category,
               ROUND(SUM(sales), 2) AS total_sales
        FROM orders
        GROUP BY month, category
        ORDER BY month, category;
    """, conn)


if __name__ == "__main__":
    conn = get_conn()
    print("\n=== Monthly Revenue ===")
    print(monthly_revenue(conn).tail())
    print("\n=== Top 10 Products by Profit ===")
    print(top_products(conn))
    print("\n=== Regional Performance ===")
    print(regional_performance(conn))
    print("\n=== Customers Inactive > 180 days ===")
    rec = customer_recency(conn)
    print(rec[rec.days_inactive > 180].head())
    print("\n=== RFM Segments (sample) ===")
    print(customer_rfm_segments(conn).head())
    conn.close()
