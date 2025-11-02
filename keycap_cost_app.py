import streamlit as st
import pandas as pd

# -----------------------------
# Configuration
# -----------------------------
USD_TO_INR = 90.51799464

# Product data (base values)
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
# Sidebar – adjustable parameters
# -----------------------------
st.sidebar.header("Adjust Extra Costs (USD / INR)")

shipping = st.sidebar.number_input("Shipping (USD)", value=85.0, step=1.0)
fees = st.sidebar.number_input("Fees (USD)", value=6.67, step=0.5)
extra_inr_1 = st.sidebar.number_input("Extra 1 (INR)", value=360.62, step=10.0)
extra_inr_2 = st.sidebar.number_input("Extra 2 (INR)", value=242.24, step=10.0)
delivery_inr = st.sidebar.number_input("Delivery (INR)", value=4680.0, step=50.0)

# Convert INR extras to USD
extra_usd = (extra_inr_1 + extra_inr_2 + delivery_inr) / USD_TO_INR

# -----------------------------
# Core calculation
# -----------------------------
total_product_usd = df["Base USD"].sum()
total_extras_usd = shipping + fees + extra_usd
ratio = 1 + (total_extras_usd / total_product_usd)

df["Final USD"] = df["Base USD"] * ratio
df["Final INR"] = df["Final USD"] * USD_TO_INR

# Totals
total_usd = df["Final USD"].sum()
total_inr = df["Final INR"].sum()

# -----------------------------
# Display
# -----------------------------
st.title("💻 Keyboard Keycap Cost Distributor")
st.write("Adjust shipping, fees, and delivery charges — values update instantly while keeping totals balanced.")

st.metric("Current Ratio (Multiplier)", f"{ratio:.4f}")
st.metric("Grand Total (INR)", f"₹{total_inr:,.2f}")

st.dataframe(df.style.format({
    "Base USD": "{:.2f}",
    "Final USD": "{:.2f}",
    "Final INR": "₹{:.2f}"
}))

# -----------------------------
# Export option
# -----------------------------
excel = df.copy()
excel["USD→INR rate"] = USD_TO_INR

excel_bytes = excel.to_excel(index=False, engine="openpyxl")
st.download_button("📥 Download Excel", data=excel_bytes, file_name="keycaps_cost_distribution.xlsx")
