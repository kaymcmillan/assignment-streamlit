import hmac
from datetime import datetime

import pandas as pd
import streamlit as st

import database as db

st.set_page_config(page_title="Order Entry App", page_icon="🛒", layout="wide")

MONEY = st.column_config.NumberColumn(format="$%.2f")


def money(value) -> str:
    return f"${float(value):,.2f}"


# ---------------------------------------------------------------- password gate
def password_gate():
    """Server-checked password. Only active if APP_PASSWORD is set in secrets."""
    try:
        expected = st.secrets.get("APP_PASSWORD")
    except Exception:
        expected = None
    if not expected or st.session_state.get("authed"):
        return
    st.title("Order Entry App")
    entered = st.text_input("Enter the class access password:", type="password")
    if st.button("Log in"):
        if hmac.compare_digest(entered, str(expected)):
            st.session_state.authed = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop()


password_gate()

# ---------------------------------------------------------------- session state
for key, default in {
    "pending": None,        # the order being reviewed
    "review_count": 0,      # changes the confirm checkbox key so it resets
    "last_order_id": None,  # most recent saved order (for verification)
    "notice": None,
    "success": None,
}.items():
    st.session_state.setdefault(key, default)

# ---------------------------------------------------------------- title
st.title("Order Entry App")
st.write(
    "Use this app to place customer orders. Pick a customer and a product, review the "
    "order, confirm it, and it is saved to Supabase and checked back from the database."
)

# ---------------------------------------------------------------- 1. display data
st.header("1. Customers and Products")
if st.button("Refresh Data"):
    st.rerun()  # the app reloads everything from Supabase on every run

try:
    customers = db.get_customers()
    products = db.get_products()
except Exception as error:
    st.error("Could not load data from Supabase. Check your secrets and table/column names.")
    st.caption(f"Details: {error}")
    st.stop()

st.caption(f"Data retrieved from Supabase at {datetime.now():%I:%M:%S %p}")

customer_col, product_col = st.columns(2)
with customer_col:
    st.subheader("Customers")
    st.dataframe(
        customers.rename(columns={db.C_ID: "Customer ID", db.C_NAME: "Name"}),
        hide_index=True,
        use_container_width=True,
    )
with product_col:
    st.subheader("Products")
    st.dataframe(
        products.rename(
            columns={db.P_ID: "Product ID", db.P_NAME: "Product", db.P_CATEGORY: "Category", db.P_PRICE: "Price"}
        ),
        hide_index=True,
        use_container_width=True,
        column_config={"Price": MONEY},
    )

customer_names = dict(zip(customers[db.C_ID].tolist(), customers[db.C_NAME].tolist()))
product_names = dict(zip(products[db.P_ID].tolist(), products[db.P_NAME].tolist()))

# ---------------------------------------------------------------- 2. order entry
st.header("2. Build an Order")
customer_id = st.selectbox(
    "Customer:",
    options=list(customer_names),
    format_func=lambda i: customer_names[i],
    index=None,
    placeholder="Select a customer",
)
product_id = st.selectbox(
    "Product:",
    options=list(product_names),
    format_func=lambda i: product_names[i],
    index=None,
    placeholder="Select a product",
)
quantity = st.number_input("Quantity:", min_value=0, value=1, step=1)

# If the person changes a selection after reviewing, the old review is out of date.
pending = st.session_state.pending
if pending and (
    pending["customer_id"] != customer_id
    or pending["product_id"] != product_id
    or pending["quantity"] != quantity
):
    st.session_state.pending = pending = None
    st.info("Your selections changed, so please review the order again.")

if st.button("Review order"):
    problems = []
    if customer_id is None:
        problems.append("Please select an existing customer.")
    if product_id is None:
        problems.append("Please select an existing product.")
    if quantity < 1:
        problems.append("Quantity must be a whole number of at least 1.")
    for problem in problems:
        st.error(problem)
    if not problems:
        try:
            price = db.get_product_price(product_id)
        except Exception as error:
            st.error(f"Could not retrieve the product price: {error}")
        else:
            st.session_state.review_count += 1
            st.session_state.success = None
            st.session_state.pending = {
                "customer_id": customer_id,
                "product_id": product_id,
                "quantity": int(quantity),
                "unit_price": price,
            }
            st.rerun()

# ---------------------------------------------------------------- 3. confirm + save
st.header("3. Review and Save")

if st.session_state.notice:
    st.warning(st.session_state.notice)
    st.session_state.notice = None
if st.session_state.success:
    st.success(st.session_state.success)

pending = st.session_state.pending
if pending is None:
    st.info("Review an order above to see its details here.")
else:
    total = round(pending["unit_price"] * pending["quantity"], 2)
    st.table(
        pd.DataFrame(
            [
                {
                    "Customer": customer_names[pending["customer_id"]],
                    "Product": product_names[pending["product_id"]],
                    "Quantity": pending["quantity"],
                    "Unit Price": money(pending["unit_price"]),
                    "Total Price": money(total),
                }
            ]
        )
    )
    confirmed = st.checkbox(
        "I confirm this order is correct and should be saved.",
        key=f"confirm_{st.session_state.review_count}",
    )
    if st.button("Submit order"):
        if not confirmed:
            st.error("Please check the confirmation box before submitting. No order was saved.")
        else:
            try:
                current_price = db.get_product_price(pending["product_id"])
            except Exception as error:
                st.error(f"Could not re-check the price, so nothing was saved: {error}")
                st.stop()

            if round(current_price, 2) != round(pending["unit_price"], 2):
                # Price changed while reviewing: show the new price, ask again.
                st.session_state.notice = (
                    f"The price changed from {money(pending['unit_price'])} to {money(current_price)}. "
                    "Please review the updated order and confirm again."
                )
                pending["unit_price"] = current_price
                st.session_state.review_count += 1  # resets the checkbox
                st.rerun()

            try:
                new_id = db.insert_order(
                    pending["customer_id"], pending["product_id"], pending["quantity"], pending["unit_price"]
                )
            except Exception as error:
                st.error(f"The order could not be saved: {error}")  # pending stays; no retry loop
            else:
                st.session_state.pending = None  # prevents a second insert on rerun
                st.session_state.last_order_id = new_id
                st.session_state.success = f"Order saved! Your new order ID is {new_id}."
                st.rerun()

# ---------------------------------------------------------------- 4. verify + history
st.header("4. Verify Saved Order")
order_id = st.session_state.last_order_id
if order_id is None:
    st.info("Save an order to see it verified here.")
else:
    try:
        saved = db.get_order(order_id)  # fresh query by ID
    except Exception as error:
        saved = None
        st.error(f"The order was saved (ID {order_id}) but could not be verified: {error}")
    else:
        if saved.empty:
            st.error(
                f"Order {order_id} was reported as saved but was not found when we looked it up. "
                "It was NOT automatically submitted again. Please check Supabase."
            )
        else:
            st.success(f"Order {order_id} was retrieved from Supabase.")
            st.dataframe(
                db.format_orders(saved, customers, products),
                hide_index=True,
                use_container_width=True,
                column_config={"Unit Price": MONEY, "Total": MONEY},
            )

st.subheader("Order History")
try:
    history = db.format_orders(db.get_order_history(), customers, products)
except Exception as error:
    st.error(f"Could not load order history: {error}")
else:
    st.dataframe(
        history,
        hide_index=True,
        use_container_width=True,
        column_config={"Unit Price": MONEY, "Total": MONEY},
    )
