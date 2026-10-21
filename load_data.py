"""
Loads data/sales_data.csv into sales.db (SQLite), after applying schema.sql.
"""
import sqlite3
import pandas as pd

DB_PATH = "sales.db"

conn = sqlite3.connect(DB_PATH)
with open("schema.sql") as f:
    conn.executescript(f.read())

df = pd.read_csv("data/sales_data.csv")

customers = df[["customer_id", "customer_name", "region"]].drop_duplicates(subset="customer_id")
orders = df[["order_id", "order_date", "customer_id", "category", "product_name",
             "quantity", "unit_price", "sales", "profit"]]

customers.to_sql("customers", conn, if_exists="append", index=False)
orders.to_sql("orders", conn, if_exists="append", index=False)

conn.commit()

n_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
n_orders = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
print(f"Loaded {n_customers} customers, {n_orders} orders into {DB_PATH}")

conn.close()
