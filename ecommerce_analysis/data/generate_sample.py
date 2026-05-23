"""
生成 3 个月示例数据，用于本地测试。
运行: python -m data.generate_sample
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
CHANNELS = ["social", "search", "email", "affiliate"]
CLUSTERS = ["high_value", "at_risk", "new"]
CATEGORIES = ["Electronics", "Home", "Fashion"]


def generate_sample(output_dir: str = "sample_data") -> None:
    os.makedirs(output_dir, exist_ok=True)
    n_users = 200
    users = []
    for i in range(n_users):
        users.append(
            {
                "customer_id": f"U{i:04d}",
                "country": RNG.choice(["CN", "US", "UK"]),
                "age": int(RNG.integers(18, 55)),
                "gender": RNG.choice(["M", "F"]),
                "days_since_last_purchase": int(RNG.integers(1, 90)),
                "AOV": round(float(RNG.uniform(80, 400)), 2),
                "total_spend": round(float(RNG.uniform(200, 3000)), 2),
                "total_order": int(RNG.integers(1, 15)),
                "acquisition_channel": RNG.choice(CHANNELS),
                "avg_review_score": round(float(RNG.uniform(3.5, 5)), 2),
                "return_rate": round(float(RNG.uniform(0, 0.2)), 3),
                "churned": int(RNG.choice([0, 1], p=[0.8, 0.2])),
                "cluster": RNG.choice(CLUSTERS),
            }
        )
    users_df = pd.DataFrame(users)

    products = []
    for cat in CATEGORIES:
        for j in range(3):
            products.append(
                {
                    "category": cat,
                    "product_name": f"{cat} Item {j+1}",
                    "total_orders": int(RNG.integers(100, 2000)),
                    "total_revenue": round(float(RNG.uniform(50000, 500000)), 2),
                    "avg_price": round(float(RNG.uniform(50, 500)), 2),
                    "avg_discount_rate": round(float(RNG.uniform(0.05, 0.25)), 3),
                    "return_rate": round(float(RNG.uniform(0.02, 0.15)), 3),
                    "avg_rating": round(float(RNG.uniform(3.8, 4.9)), 2),
                }
            )
    products_df = pd.DataFrame(products)

    dates = pd.date_range("2024-01-01", "2024-03-31", freq="D")
    orders = []
    oid = 0
    for d in dates:
        n = int(RNG.integers(3, 12))
        for _ in range(n):
            uid = f"U{RNG.integers(0, n_users):04d}"
            cat = RNG.choice(CATEGORIES)
            prod = f"{cat} Item {RNG.integers(1, 4)}"
            orders.append(
                {
                    "order_id": f"O{oid:06d}",
                    "customer_id": uid,
                    "order_date": d.strftime("%Y-%m-%d"),
                    "category": cat,
                    "product_name": prod,
                    "discount_rate": round(float(RNG.uniform(0, 0.3)), 3),
                    "total_amount": round(float(RNG.uniform(50, 600)), 2),
                    "customer_rating": round(float(RNG.uniform(3, 5)), 1),
                    "returned": int(RNG.choice([0, 1], p=[0.92, 0.08])),
                }
            )
            oid += 1
    orders_df = pd.DataFrame(orders)

    users_df.to_csv(os.path.join(output_dir, "users.csv"), index=False)
    products_df.to_csv(os.path.join(output_dir, "products.csv"), index=False)
    orders_df.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
    print(f"Sample data written to {output_dir}/")


if __name__ == "__main__":
    generate_sample()
