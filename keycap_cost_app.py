import streamlit as st
import pandas as pd
import io

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
# Initialize the editable column, copying from Base USD
df["Editable USD"] = df["Base USD"]

# -----------------------------
# Sidebar – adjustable global values
# -----------------------------
st.sidebar.header("⚙️ Adjust Extra Costs (USD / INR)")

shipping = st.sidebar.number_input("Shipping (USD)", value=85.0, step=1.0)
fees = st.sidebar.number_input("Fees (USD)", value=6.67, step=0.5)
extra_inr_1 = st.sidebar.number_input("Extra 1 (INR)", value=360.62, step=10.0)
extra_inr_2 = st.sidebar.number_input("Extra 2 (INR)", value=242.24, step=10.0)
delivery_inr = st.sidebar.number_input("Delivery (INR)", value=4680.0, step=50.0)

# Calculate total extra USD
extra_usd = (extra_inr_1 + extra_inr_2 + delivery_inr) / USD_TO_INR
total_extra_usd = shipping + fees + extra_usd

# -----------------------------
# Product Editing Section
# -----------------------------
st.title("💻 Adjustable Product Cost Distributor (Smart Mode)")

st.write(f"""
The current USD to INR exchange rate used is: **{USD_TO_INR:.4f}**.  
Total extra cost to distribute: **${total_extra_usd:,.2f}**
""")

# Editable table
# We pass the relevant columns (Product and Editable USD) to the editor
editor_df = df[["Product", "Editable USD"]].copy()

# Use st.data_editor (the correct, modern function)
edited_data = st.data_editor(
    editor_df,
    key="editable_prices",
    num_rows="fixed",
    use_container_width=True,
    column_config={
        "Product": st.column_config.TextColumn(
            "Product",
            disabled=True, # Prevent editing the product name
            width="large"
        ),
        "Editable USD": st.column_config.NumberColumn(
            "Base USD (Editable)",
            help="The base price of the product in USD",
            format="%.2f",
            width="small"
        ),
    }
)

# Update the main DataFrame's 'Editable USD' column with the user's changes
df["Editable USD"] = edited_data["Editable USD"]

# Fixed items selection
fixed_items = st.multiselect(
    "🔒 Select products to keep fixed (No extra costs added to these):",
    options=df["Product"].tolist(),
    default=[]
)

# -----------------------------
# Core Calculation Logic
# -----------------------------
total_product_usd = df["Editable USD"].sum()
total_usd = total_product_usd + total_extra_usd

# If some products are fixed, adjust others proportionally
df["Final USD"] = df["Editable USD"]

if fixed_items:
    fixed_sum = df[df["Product"].isin(fixed_items)]["Editable USD"].sum()
    variable_df = df[~df["Product"].isin(fixed_items)]
    variable_sum = variable_df["Editable USD"].sum()

    # The total cost to distribute is Total Extra Cost + Sum of Variable Items
    new_variable_total = total_extra_usd + variable_sum

    if variable_sum > 0:
        ratio = new_variable_total / variable_sum
        # Apply ratio only to non-fixed items
        df.loc[~df["Product"].isin(fixed_items), "Final USD"] *= ratio
    else:
        # If variable sum is zero, extra costs cannot be distributed
        ratio = 1
        st.warning("All products are fixed. Extra costs are not distributed and are not accounted for in individual product totals.")
else:
    # Distribute over all items
    if total_product_usd > 0:
        ratio = 1 + (total_extra_usd / total_product_usd)
        df["Final USD"] = df["Editable USD"] * ratio
    else:
        ratio = 1
        st.error("Total product cost is zero. Cannot calculate distribution ratio.")


df["Final INR"] = df["Final USD"] * USD_TO_INR

# -----------------------------
# Display
# -----------------------------
st.subheader("📊 Final Results and Cost Distribution")

col1, col2, col3 = st.columns(3)
col1.metric("Distribution Ratio (Factor)", f"{ratio:.4f}")
col2.metric("Grand Total (USD)", f"${df['Final USD'].sum():,.2f}")
col3.metric("Grand Total (INR)", f"₹{df['Final INR'].sum():,.2f}")

st.dataframe(df.style.format({
    "Base USD": "${:.2f}",
    "Editable USD": "${:.2f}",
    "Final USD": "${:.2f}",
    "Final INR": "₹{:.2f}"
}), use_container_width=True)

# -----------------------------
# Export option
# -----------------------------
excel = df.copy()
excel.rename(columns={"Base USD": "Original Base USD"}, inplace=True)
excel["USD→INR rate"] = USD_TO_INR

# Convert DataFrame to Excel bytes
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    excel.to_excel(writer, index=False, sheet_name='Cost_Distribution')
    
excel_bytes = output.getvalue()

st.download_button(
    "📥 Download Updated Excel", 
    data=excel_bytes, 
    file_name="keycap_cost_dashboard.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
