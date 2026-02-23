import streamlit as st

st.set_page_config(
    page_title="Capital Project Revenue Impact Calculator",
    page_icon="🧮",
    layout="wide",
)

st.title("Capital Project Revenue Impact Calculator")

# --- Inputs ---
project_value = st.number_input("Capital Project Value (£)", min_value=0, value=10000000, step=100000)
financing_method = st.selectbox("Financing Method", ["Borrowing", "Internal Borrowing", "Capital Receipts", "Grants / Contributions"])

if financing_method in ["Borrowing", "Internal Borrowing"]:
    st.subheader("Borrowing Assumptions")
    interest_rate = st.slider("Interest Rate (%)", min_value=0.0, max_value=10.0, value=4.5, step=0.1)
    asset_life = st.slider("Asset Life (years)", min_value=1, max_value=60, value=40, step=1)
    mrp_method = st.selectbox("MRP Method", ["Annuity", "Straight Line"])

# --- Calculation ---
annual_mrp = 0
annual_interest_cost = 0

if financing_method == "Borrowing":
    if mrp_method == "Straight Line":
        annual_mrp = project_value / asset_life
    elif mrp_method == "Annuity":
        i = interest_rate / 100
        n = asset_life
        if i > 0:
            annual_mrp = project_value * (i * (1 + i)**n) / ((1 + i)**n - 1)
        else:
            annual_mrp = project_value / asset_life
    annual_interest_cost = project_value * (interest_rate / 100)

elif financing_method == "Internal Borrowing":
    # Similar to borrowing, but might have different interest rate implications (opportunity cost)
    if mrp_method == "Straight Line":
        annual_mrp = project_value / asset_life
    elif mrp_method == "Annuity":
        i = interest_rate / 100
        n = asset_life
        if i > 0:
            annual_mrp = project_value * (i * (1 + i)**n) / ((1 + i)**n - 1)
        else:
            annual_mrp = project_value / asset_life
    annual_interest_cost = project_value * (interest_rate / 100) # Opportunity cost of not investing the cash

total_annual_cost = annual_mrp + annual_interest_cost

# --- Output ---
st.subheader("Calculated Annual Revenue Impact")
st.metric("Annual MRP Cost", f"£{annual_mrp:,.2f}")
st.metric("Annual Interest Cost", f"£{annual_interest_cost:,.2f}")
st.metric("Total Annual Revenue Financing Cost", f"£{total_annual_cost:,.2f}")

# --- Integration with MTFS ---
if st.button("Add to MTFS"):
    # This part will be implemented later.
    # It will update the session state with the new costs,
    # which will then be picked up by the main MTFS model.
    st.success("Project added to MTFS (functionality to be implemented).")
