"""
Generates a synthetic retail sales dataset (legit, self-contained — no external download needed).
Output: data/sales_data.csv
"""
import csv
import random
from datetime import date, timedelta

random.seed(42)

CATEGORIES = {
    "Electronics": ["Laptop", "Headphones", "Monitor", "Keyboard", "Webcam"],
    "Furniture": ["Office Chair", "Desk", "Bookshelf", "Filing Cabinet"],
    "Stationery": ["Notebook", "Pen Set", "Whiteboard", "Sticky Notes"],
    "Appliances": ["Coffee Maker", "Microwave", "Desk Fan", "Air Purifier"],
}

REGIONS = ["North", "South", "East", "West"]

NUM_CUSTOMERS = 300
NUM_ORDERS = 8000
START_DATE = date(2023, 1, 1)
END_DATE = date(2025, 9, 1)

def random_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

customers = [
    {"customer_id": i, "customer_name": f"Customer_{i}", "region": random.choice(REGIONS)}
    for i in range(1, NUM_CUSTOMERS + 1)
]

rows = []
order_id = 1
for _ in range(NUM_ORDERS):
    category = random.choice(list(CATEGORIES.keys()))
    product = random.choice(CATEGORIES[category])
    customer = random.choice(customers)
    order_date = random_date(START_DATE, END_DATE)
    quantity = random.randint(1, 6)
    unit_price = round(random.uniform(200, 15000), 2)
    sales = round(unit_price * quantity, 2)
    cost_ratio = random.uniform(0.55, 0.85)
    profit = round(sales * (1 - cost_ratio), 2)

    rows.append({
        "order_id": order_id,
        "order_date": order_date.isoformat(),
        "customer_id": customer["customer_id"],
        "customer_name": customer["customer_name"],
        "region": customer["region"],
        "category": category,
        "product_name": product,
        "quantity": quantity,
        "unit_price": unit_price,
        "sales": sales,
        "profit": profit,
    })
    order_id += 1

with open("data/sales_data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} orders -> data/sales_data.csv")
