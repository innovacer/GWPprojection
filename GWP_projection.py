import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# ------------------------------
# 1. SET PAGE CONFIG AND STYLES
# ------------------------------
st.set_page_config(
    page_title="GWP Projection App",
    layout="wide",  # 'centered' or 'wide'
    initial_sidebar_state="expanded"
)

# Custom CSS for a more engaging UI (optional)
st.markdown("""
<style>
.sidebar .sidebar-content {
    background-color: #f8f9fa;
}
.main {
    color: #000;
    background-color: #fff;
}
h1, h2, h3 {
    font-family: "Arial", sans-serif;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# 2. INTRODUCTION & HEADER
# -------------------------
st.title("GWP Projection Methodology Tool")
st.write("""
This interactive tool demonstrates the **Gross Written Premium (GWP)** projection steps 
for **Life and Non-Life** lines over a 5-year horizon, in line with the **CAS** standards 
and the detailed methodology specified in the final submission paper.
""")

# -------------------------------
# 3. USER INPUTS: SIDEBAR WIDGETS
# -------------------------------
st.sidebar.title("Input Parameters")

# Baseline GWP (Year t)
default_gwp_life = st.sidebar.number_input(
    "Current (Year t) GWP - Life (in millions)", min_value=0.0, value=100.0, step=10.0
)
default_gwp_non_life = st.sidebar.number_input(
    "Current (Year t) GWP - Non-Life (in millions)", min_value=0.0, value=200.0, step=10.0
)

st.sidebar.markdown("---")

# Economic Inputs
gdp_growth = st.sidebar.slider(
    "GDP Growth Rate (%)", min_value=-5.0, max_value=10.0, value=3.0, step=0.1
)
inflation_rate = st.sidebar.slider(
    "Inflation Rate (%)", min_value=0.0, max_value=15.0, value=2.0, step=0.1
)
historical_trend_factor = st.sidebar.slider(
    "Historical Trend Factor (%)", min_value=-2.0, max_value=10.0, value=2.0, step=0.1
)

st.sidebar.markdown("---")

# Attritional Loss & Expenses
attritional_loss_ratio = st.sidebar.slider(
    "Attritional Loss Ratio (%)", min_value=0.0, max_value=100.0, value=60.0, step=1.0
)
expense_ratio = st.sidebar.slider(
    "Expense Ratio (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0
)

st.sidebar.markdown("---")

# Churn & New Business
churn_rate = st.sidebar.slider(
    "Customer Churn Rate (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0
)
new_business_rate = st.sidebar.slider(
    "New Business Growth Rate (%)", min_value=0.0, max_value=50.0, value=5.0, step=1.0
)

st.sidebar.markdown("---")

# Scenario Adjustments
catastrophic_impact = st.sidebar.slider(
    "Catastrophic Events Impact (%)", min_value=0.0, max_value=50.0, value=5.0, step=1.0
)
economic_downturn_impact = st.sidebar.slider(
    "Economic Downturn Impact (%)", min_value=0.0, max_value=50.0, value=3.0, step=1.0
)

st.sidebar.markdown("---")

# Regulatory and Technological
regulatory_impact = st.sidebar.slider(
    "Regulatory Changes Impact (%)", min_value=-10.0, max_value=10.0, value=1.0, step=0.5
)
tech_impact = st.sidebar.slider(
    "Technological Advancements Impact (%)", min_value=-10.0, max_value=10.0, value=2.0, step=0.5
)

st.sidebar.markdown("---")

# ---------------------------
# 4. HELPER FUNCTIONS
# ---------------------------
def calculate_gwp_projection(
    gwp_life_base,
    gwp_non_life_base,
    gdp,
    inflation,
    hist_trend,
    loss_ratio,
    expense_ratio,
    churn,
    new_business,
    cat_impact,
    econ_downturn,
    reg_impact,
    tech_impact
):
    """
    Calculate year-by-year GWP for Life and Non-Life over 5 years
    following the 6-step methodology.
    Returns a DataFrame with columns:
    [Year, GWP_Life, GWP_NonLife]
    """
    
    # Convert percentages to decimal multipliers
    gdp_dec = gdp / 100.0
    inflation_dec = inflation / 100.0
    hist_trend_dec = hist_trend / 100.0
    loss_ratio_dec = loss_ratio / 100.0
    expense_ratio_dec = expense_ratio / 100.0
    churn_dec = churn / 100.0
    new_business_dec = new_business / 100.0
    cat_impact_dec = cat_impact / 100.0
    econ_downturn_dec = econ_downturn / 100.0
    reg_impact_dec = reg_impact / 100.0
    tech_impact_dec = tech_impact / 100.0
    
    # Initialize results storage
    results = []
    
    # Starting GWP for year t
    gwp_life_current = gwp_life_base
    gwp_non_life_current = gwp_non_life_base
    
    for year in range(1, 6):
        # -------------------------
        # Step 1: Base Growth Model
        # -------------------------
        base_life = gwp_life_current * (1 + gdp_dec + inflation_dec) * (1 + hist_trend_dec)
        base_non_life = gwp_non_life_current * (1 + gdp_dec + inflation_dec) * (1 + hist_trend_dec)
        
        # ------------------------------------------------
        # Step 2: Attritional Loss + Expense Adjustments
        # ------------------------------------------------
        # For illustration, we reduce GWP by the attritional loss ratio,
        # then re-add expense and profit load. 
        # Alternatively, you can incorporate expense as part of the margin.
        
        # Illustrative approach:
        loss_adjustment_factor = 1 - loss_ratio_dec
        expense_adjustment_factor = 1 - expense_ratio_dec
        
        # Combined factor (simplified)
        combined_adjustment_factor = loss_adjustment_factor * expense_adjustment_factor
        
        adj_base_life = base_life * combined_adjustment_factor
        adj_base_non_life = base_non_life * combined_adjustment_factor
        
        # -------------------------------------------
        # Step 3: Customer Churn & New Business
        # -------------------------------------------
        retention_rate = 1 - churn_dec
        net_growth_factor = retention_rate + new_business_dec
        
        adj_life_churn = adj_base_life * net_growth_factor
        adj_non_life_churn = adj_base_non_life * net_growth_factor
        
        # -------------------------------------------
        # Step 4: Scenario-Based Adjustments
        # -------------------------------------------
        scenario_impact_factor_life = 1 - (cat_impact_dec + econ_downturn_dec)
        scenario_impact_factor_non_life = 1 - (cat_impact_dec + econ_downturn_dec)
        
        # Cap the scenario factor at a minimum to avoid negative
        scenario_impact_factor_life = max(scenario_impact_factor_life, 0.0)
        scenario_impact_factor_non_life = max(scenario_impact_factor_non_life, 0.0)
        
        life_after_scenario = adj_life_churn * scenario_impact_factor_life
        non_life_after_scenario = adj_non_life_churn * scenario_impact_factor_non_life
        
        # -------------------------------------------
        # Step 5: Regulatory & Technological Adjustments
        # -------------------------------------------
        reg_tech_multiplier = (1 + reg_impact_dec) * (1 + tech_impact_dec)
        
        final_gwp_life = life_after_scenario * reg_tech_multiplier
        final_gwp_non_life = non_life_after_scenario * reg_tech_multiplier
        
        # -------------------------------------------
        # Step 6: Iterative Projection
        # -------------------------------------------
        # The final GWP for year j becomes the starting point for year j+1.
        gwp_life_current = final_gwp_life
        gwp_non_life_current = final_gwp_non_life
        
        # Store results
        results.append({
            "Year": f"t+{year}",
            "GWP_Life (millions)": round(final_gwp_life, 2),
            "GWP_Non-Life (millions)": round(final_gwp_non_life, 2)
        })
    
    return pd.DataFrame(results)

# --------------------------------------
# 5. PERFORM CALCULATION & SHOW RESULTS
# --------------------------------------
df_results = calculate_gwp_projection(
    gwp_life_base=default_gwp_life,
    gwp_non_life_base=default_gwp_non_life,
    gdp=gdp_growth,
    inflation=inflation_rate,
    hist_trend=historical_trend_factor,
    loss_ratio=attritional_loss_ratio,
    expense_ratio=expense_ratio,
    churn=churn_rate,
    new_business=new_business_rate,
    cat_impact=catastrophic_impact,
    econ_downturn=economic_downturn_impact,
    reg_impact=regulatory_impact,
    tech_impact=tech_impact
)

# Show the results in a data table
st.subheader("Projection Results (5-Year Horizon)")
st.dataframe(df_results)

# ----------------------------
# 6. VISUALIZATIONS: ALT Charts
# ----------------------------
st.subheader("Visualize the Projected GWP")

# Melt the DF for easy plotting in Altair
df_melted = df_results.melt(id_vars="Year", var_name="Line", value_name="GWP")

chart = (
    alt.Chart(df_melted, title="Projected GWP over 5 Years")
    .mark_line(point=True)
    .encode(
        x="Year:N",
        y=alt.Y("GWP:Q", title="GWP (millions)"),
        color="Line:N",
        tooltip=["Year:N", "Line:N", "GWP:Q"]
    )
    .interactive()
)

st.altair_chart(chart, use_container_width=True)

st.write("""
**Interpretation:**
- The chart above shows the year-by-year evolution of Life and Non-Life GWP 
  under the current input assumptions. 
- Use the sliders in the sidebar to adjust macroeconomic, underwriting, 
  and scenario inputs to see how GWP projections shift in real-time.
""")

# ----------------------
# 7. ADDITIONAL COMMENTS
# ----------------------
st.markdown("""
### Disclaimers and Limitations
- This tool implements a **simplified** version of the 6-step methodology 
  from the final GWP Projection Paper. 
- **Real-world complexities**, such as segmented underwriting and 
  stochastic catastrophe modeling, may require more advanced treatment.
- All results are **illustrative** and should be reviewed by a **qualified actuary** 
  before final regulatory submissions.
""")

st.success("Adjust the inputs on the left sidebar to explore different scenarios!")
