"""三张业务表的列定义与模板数据"""
from __future__ import annotations

import pandas as pd

USER_COLUMNS = {
    "customer_id": "str",
    "country": "str",
    "age": "int",
    "gender": "str",
    "days_since_last_purchase": "int",
    "AOV": "float",
    "total_spend": "float",
    "total_order": "int",
    "acquisition_channel": "str",
    "avg_review_score": "float",
    "return_rate": "float",
    "churned": "int",
    "cluster": "str",
}

PRODUCT_COLUMNS = {
    "category": "str",
    "product_name": "str",
    "total_orders": "int",
    "total_revenue": "float",
    "avg_price": "float",
    "avg_discount_rate": "float",
    "return_rate": "float",
    "avg_rating": "float",
}

ORDER_COLUMNS = {
    "order_id": "str",
    "customer_id": "str",
    "order_date": "str",
    "category": "str",
    "product_name": "str",
    "discount_rate": "float",
    "total_amount": "float",
    "customer_rating": "float",
    "returned": "int",
}

USER_COLUMN_DOCS = """
| 列名 | 类型 | 说明 |
|------|------|------|
| customer_id | str | 用户唯一 ID |
| country | str | 国家/地区 |
| age | int | 年龄 |
| gender | str | 性别 |
| days_since_last_purchase | int | 距上次购买天数 |
| AOV | float | 历史平均客单价 |
| total_spend | float | 累计消费 |
| total_order | int | 累计订单数 |
| acquisition_channel | str | 获客渠道 |
| avg_review_score | float | 平均评分 |
| return_rate | float | 退货率 |
| churned | int | 是否流失 0/1 |
| cluster | str | 用户分层标签 |
"""

PRODUCT_COLUMN_DOCS = """
| 列名 | 类型 | 说明 |
|------|------|------|
| category | str | 品类 |
| product_name | str | 产品名称 |
| total_orders | int | 累计销量 |
| total_revenue | float | 累计营收 |
| avg_price | float | 平均售价 |
| avg_discount_rate | float | 平均折扣率 |
| return_rate | float | 退货率 |
| avg_rating | float | 平均评分 |
"""

ORDER_COLUMN_DOCS = """
| 列名 | 类型 | 说明 |
|------|------|------|
| order_id | str | 订单 ID |
| customer_id | str | 用户 ID |
| order_date | str | 下单日期 YYYY-MM-DD |
| category | str | 品类 |
| product_name | str | 产品名称 |
| discount_rate | float | 折扣率 0-1 |
| total_amount | float | 订单金额 |
| customer_rating | float | 评分 |
| returned | int | 是否退货 0/1 |
"""


def get_template_dfs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """返回三张表的示例 DataFrame，用于下载模板。"""
    users = pd.DataFrame(
        [
            {
                "customer_id": "U001",
                "country": "CN",
                "age": 28,
                "gender": "F",
                "days_since_last_purchase": 5,
                "AOV": 320.5,
                "total_spend": 1280.0,
                "total_order": 4,
                "acquisition_channel": "social",
                "avg_review_score": 4.6,
                "return_rate": 0.05,
                "churned": 0,
                "cluster": "high_value",
            },
            {
                "customer_id": "U002",
                "country": "US",
                "age": 35,
                "gender": "M",
                "days_since_last_purchase": 45,
                "AOV": 180.0,
                "total_spend": 540.0,
                "total_order": 3,
                "acquisition_channel": "search",
                "avg_review_score": 4.2,
                "return_rate": 0.12,
                "churned": 1,
                "cluster": "at_risk",
            },
        ]
    )

    products = pd.DataFrame(
        [
            {
                "category": "Electronics",
                "product_name": "Smart Watch Pro",
                "total_orders": 1200,
                "total_revenue": 480000.0,
                "avg_price": 400.0,
                "avg_discount_rate": 0.1,
                "return_rate": 0.08,
                "avg_rating": 4.5,
            },
            {
                "category": "Home",
                "product_name": "Air Purifier X",
                "total_orders": 800,
                "total_revenue": 240000.0,
                "avg_price": 300.0,
                "avg_discount_rate": 0.15,
                "return_rate": 0.06,
                "avg_rating": 4.3,
            },
        ]
    )

    orders = pd.DataFrame(
        [
            {
                "order_id": "O1001",
                "customer_id": "U001",
                "order_date": "2024-01-05",
                "category": "Electronics",
                "product_name": "Smart Watch Pro",
                "discount_rate": 0.1,
                "total_amount": 360.0,
                "customer_rating": 4.8,
                "returned": 0,
            },
            {
                "order_id": "O1002",
                "customer_id": "U002",
                "order_date": "2024-02-12",
                "category": "Home",
                "product_name": "Air Purifier X",
                "discount_rate": 0.2,
                "total_amount": 240.0,
                "customer_rating": 4.0,
                "returned": 1,
            },
        ]
    )
    return users, products, orders


def empty_template_df(table: str) -> pd.DataFrame:
    """返回仅含表头的空模板。"""
    mapping = {
        "users": USER_COLUMNS,
        "products": PRODUCT_COLUMNS,
        "orders": ORDER_COLUMNS,
    }
    cols = mapping[table]
    return pd.DataFrame(columns=list(cols.keys()))


if __name__ == "__main__":
    u, p, o = get_template_dfs()
    print("Users:", u.shape)
    print("Products:", p.shape)
    print("Orders:", o.shape)
