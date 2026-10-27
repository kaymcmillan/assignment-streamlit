"""Supabase helper functions for the Order Entry app."""
from datetime import date

import pandas as pd
import streamlit as st
from supabase import Client, create_client

# ---------------------------------------------------------------------------
# EDIT THESE to match your Supabase tables from the previous assignment.
# Open Supabase > Table Editor and compare the column names exactly.
# ---------------------------------------------------------------------------
CUSTOMERS, PRODUCTS, ORDERS = "customers", "products", "orders"

C_ID, C_NAME = "customer_id", "name"
P_ID, P_NAME, P_CATEGORY, P_PRICE = "product_id", "product_name", "category", "price"
O_ID, O_CUSTOMER, O_PRODUCT = "order_id", "customer_id", "product_id"
O_QTY, O_UNIT, O_DATE = "quantity", "unit_price", "order_date"
# If your orders table also has a stored total column, put its name here
# (e.g. "total_price"). Leave as None if it does not.
O_TOTAL = None


@st.cache_resource
def get_client() -> Client:
    """Create the Supabase connection once, using credentials from secrets."""
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def get_customers() -> pd.DataFrame:
    rows = get_client().table(CUSTOMERS).select(f"{C_ID},{C_NAME}").order(C_ID).execute().data
    return pd.DataFrame(rows, columns=[C_ID, C_NAME])


def get_products() -> pd.DataFrame:
    cols = f"{P_ID},{P_NAME},{P_CATEGORY},{P_PRICE}"
    rows = get_client().table(PRODUCTS).select(cols).order(P_ID).execute().data
    return pd.DataFrame(rows, columns=[P_ID, P_NAME, P_CATEGORY, P_PRICE])


def get_product_price(product_id) -> float:
    """Always ask Supabase for the CURRENT price of one product."""
    rows = get_client().table(PRODUCTS).select(P_PRICE).eq(P_ID, product_id).execute().data
    if not rows:
        raise ValueError("That product no longer exists.")
    return float(rows[0][P_PRICE])


def insert_order(customer_id, product_id, quantity: int, unit_price: float) -> int:
    """Insert one order. The database generates the order ID; we return it."""
    record = {
        O_CUSTOMER: customer_id,
        O_PRODUCT: product_id,
        O_QTY: int(quantity),
        O_UNIT: round(float(unit_price), 2),
        O_DATE: date.today().isoformat(),
    }
    if O_TOTAL:
        record[O_TOTAL] = round(float(unit_price) * int(quantity), 2)
    result = get_client().table(ORDERS).insert(record).execute()
    if not result.data:
        raise RuntimeError("Supabase did not return the new order.")
    return result.data[0][O_ID]


def get_order(order_id) -> pd.DataFrame:
    """NEW query that looks up one saved order by its ID (used for verification)."""
    rows = get_client().table(ORDERS).select("*").eq(O_ID, order_id).execute().data
    return pd.DataFrame(rows)


def get_order_history() -> pd.DataFrame:
    rows = get_client().table(ORDERS).select("*").order(O_ID, desc=True).execute().data
    return pd.DataFrame(rows)


def format_orders(orders: pd.DataFrame, customers: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """Turn raw order rows into a readable table with names and a computed total."""
    columns = ["Order ID", "Customer", "Product", "Quantity", "Unit Price", "Total", "Order Date"]
    if orders.empty:
        return pd.DataFrame(columns=columns)
    customer_names = dict(zip(customers[C_ID].tolist(), customers[C_NAME].tolist()))
    product_names = dict(zip(products[P_ID].tolist(), products[P_NAME].tolist()))
    table = pd.DataFrame(
        {
            "Order ID": orders[O_ID],
            "Customer": orders[O_CUSTOMER].map(customer_names),
            "Product": orders[O_PRODUCT].map(product_names),
            "Quantity": orders[O_QTY],
            "Unit Price": orders[O_UNIT].astype(float),
            "Total": (orders[O_UNIT].astype(float) * orders[O_QTY]).round(2),
            "Order Date": orders[O_DATE],
        }
    )
    return table
