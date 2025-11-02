import streamlit as st
import pandas as pd

# -----------------------------
# Constants
# -----------------------------
USD_TO_INR = 90.51799464

# Base product data
data = [
    ["Crystal Machinery Keycaps", 24.50],
    ["Multi-color PBT Keycaps – Blue", 4.20],
    ["Multi-color PBT Keycaps – Pink", 4.20],
    ["Multi-color PBT Keycaps – Red", 3.71],
    ["Multi-color PBT Keycaps – Purple", 3.71],
    ["Multi-color PBT Keycaps – Black Powder", 4.20],
    ["Multi-color PBT Keycaps – Black", 4.20],
    ["DIY Keyboard Tool", 3.00],
    ["143 Key Comic Style", 7.14],
    ["143 Key White Comic", 7.14],
    ["125 Key Sublimation (Pink)", 7.14],
    ["OUTEMU Switch (Blue)", 10.00],
    ["OUTEMU Switch (Brown)", 10.00],
    ["Magic Fog Keycap (Blue)", 7.80],
    ["Magic Fog Rainbow Mist", 7.80],
    ["Magic Fog Star Mans", 7.80],
    ["Magic Mist Roland Jade", 7.80],
    ["Magic Fog Star Purple", 23.40],
]
df = pd.DataFrame(data, columns=["Product", "Base USD"])

# -----------------------------
# Sidebar – adjustable global values
# -----------------------------
st.sidebar.header("⚙️ Adjust Extra Costs (USD / INR)")

shipping = st.sidebar.number_input("Shipping (USD)", value=85.0, step=1.0)
fees = st.sidebar.number_input("Fees (USD)", value=6.67, step=0.5)
extra_inr_1 = st.sidebar.number_input("Extra 1 (INR)", value=360.62, step=10.0)
extra_inr_2 = st.sidebar.number_input("Extra 2 (INR)", value=242.24, step=10.0)
delivery_inr = st.sidebar.number_input("Delivery (INR)", value=4680.0, step=50.0)

extra_usd = (extra_inr_1 + extra_inr_2 + delivery_inr) / USD_TO_INR

# -----------------------------
# Product Editing Section
# -----------------------------
st.title("💻 Adjustable Product Cost Distributor (Smart Mode)")

st.write("""
You can edit each product price directly.  
Mark items as **fixed** if you don’t want them to change when ratios adjust.  
Other prices will rebalance automatically to keep total cost constant.
""")

# Editable table
df["Editable USD"] = st.experimental_data_editor(
    df["Base USD"],
    key="editable_prices",
    num_rows="fixed",
    use_container_width=True
)

# Fixed items selection
fixed_items = st.multiselect(
    "🔒 Select products to keep fixed:",
    options=df["Product"].tolist(),
    default=[]
)

# -----------------------------
# Core Calculation Logic
# -----------------------------
total_product_usd = df["Editable USD"].sum()
total_extra_usd = shipping + fees + extra_usd
total_usd = total_product_usd + total_extra_usd

# If some products are fixed, adjust others proportionally
df["Final USD"] = df["Editable USD"]

if fixed_items:
    fixed_sum = df[df["Product"].isin(fixed_items)]["Editable USD"].sum()
    variable_sum = total_product_usd - fixed_sum
    new_variable_total = variable_sum + total_extra_usd
    if variable_sum > 0:
        ratio = new_variable_total / variable_sum
        df.loc[~df["Product"].isin(fixed_items), "Final USD"] *= ratio
    else:
        ratio = 1
else:
    ratio = 1 + (total_extra_usd / total_product_usd)
    df["Final USD"] = df["Editable USD"] * ratio

df["Final INR"] = df["Final USD"] * USD_TO_INR

# -----------------------------
# Display
# -----------------------------
st.subheader("📊 Results")

st.metric("Current Ratio", f"{ratio:.4f}")
st.metric("Grand Total (USD)", f"${df['Final USD'].sum():,.2f}")
st.metric("Grand Total (INR)", f"₹{df['Final INR'].sum():,.2f}")

st.dataframe(df.style.format({
    "Editable USD": "{:.2f}",
    "Final USD": "{:.2f}",
    "Final INR": "₹{:.2f}"
}))

# -----------------------------
# Export option
# -----------------------------
excel = df.copy()
excel["USD→INR rate"] = USD_TO_INR

excel_bytes = excel.to_excel(index=False, engine="openpyxl")
st.download_button("📥 Download Updated Excel", data=excel_bytes, file_name="keycap_cost_dashboard.xlsx")

