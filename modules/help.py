"""
Help & Tooltips System
Centralized help text for MTFS Budget Gap Simulator
"""

HELP_TEXT = {
    # Main Dashboard KPIs
    "cumulative_gap": "Total budget shortfall across the 4-year MTFS period. Expressed as £m (millions). RED if >25% of year 1 budget, AMBER if >10%, GREEN if sustainable.",
    "reserves_status": "Projected year when reserves become depleted if no action is taken. GREEN if reserves projected to remain above minimum threshold (5% of budget) throughout.",
    "savings_needed": "Additional savings required (beyond planned) to balance the budget without using further reserves.",
    "rag_rating": "Financial Sustainability rated as RED (unsustainable), AMBER (at-risk) or GREEN (sustainable) based on reserves, gap, and trend.",
    
    # Assumptions
    "council_tax_increase": "Annual council tax increase assumption (%). Higher = more income to offset gap pressures.",
    "business_rates_growth": "Year-on-year growth/decline in business rates income. Typically volatile. Negative = risk.",
    "grant_change": "Core government grant trend (%). Typically declining. More negative = larger gap.",
    "fees_charges_growth": "Growth in income from discretionary fees and charges (fees for services, licenses, etc.).",
    "pay_award": "Annual pay award inflation (%. Typically 2-4%. Drives largest cost pressure in most councils.",
    "general_inflation": "Non-pay cost inflation. Applied to supplies, services, contract inflation.",
    "asc_demand_growth": "Adult Social Care cost growth from demographic demand and complexity (aging population).",
    "csc_demand_growth": "Children's Social Care cost growth from demand and complexity trends.",
    
    # Policy Controls
    "savings_target": "Council's committed annual savings programme as % of net revenue budget.",
    "use_of_reserves": "How much of the gap is funded from reserves (vs. service cuts). 0% = all cuts; 100% = all reserves.",
    "protect_social_care": "If enabled, suppresses demand growth assumptions for ASC/CSC (assumes resources held constant).",
    
    # Savings Strategy
    "savings_transformation": "Savings from service transformation (process improvement, technology, restructure).",
    "savings_income": "Savings from income generation (new fees, commercialisation, trading companies).",
    "savings_demand": "Savings from demand management (prevention, early intervention, shared services).",
    
    # Sensitivity
    "council_tax_per_household": "Shows per-household impact of council tax changes. Useful for public communication.",
    
    # Stochastic
    "monte_carlo": "Monte Carlo simulation: runs multiple scenarios with random variations in assumptions to test robustness.",
    "stochastic_std": "Standard deviation (%) applied to each assumption in stochastic runs. Higher = wider uncertainty band.",
    
    # Commercial
    "capital_cost": "Upfront capital investment required for commercial project.",
    "annual_income_target": "Target recurring annual income from project (e.g., rental, dividend from trading company).",
    "operating_costs": "Annual costs to operate the project (staff, maintenance, utilities).",
    "capital_receipt": "One-off capital receipt (e.g., from asset sale) that can be used to fund revenue pressures.",
    "pwlb_rate": "Public Works Loan Board interest rate on borrowing. Used to compute debt service cost in commercial models.",
    "commercial_realisation": "Assumed % of target income achievable (80% = conservative; 100% = optimistic).",
    
    # RAG Ratings
    "rag_green": "Reserves >10% of budget, gap <5% of budget, savings delivery on track.",
    "rag_amber": "Reserves 5–10% of budget, gap 5–20% of budget, or significant delivery risk.",
    "rag_red": "Reserves <5% of budget, gap >20% of budget, or unsustainable trajectory.",
}

def get_help(key: str) -> str:
    """Get help text for a given key. Returns key if not found."""
    return HELP_TEXT.get(key, f"Help unavailable for '{key}'")

def render_help_icon(key: str):
    """Return HTML for a help icon tooltip (for use in Streamlit markdown)."""
    text = get_help(key)
    return f'<span title="{text}" style="cursor:help; color:#0066cc; font-weight:bold;">ⓘ</span>'
