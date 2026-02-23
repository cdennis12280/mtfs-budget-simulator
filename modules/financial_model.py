"""
Centralized Financial Model for the MTFS Budget Simulator.
This module contains all the core financial logic for the application.
"""
import pandas as pd
import numpy as np

class FinancialModel:
    """
    A centralized class to handle all financial calculations for the MTFS simulator.
    """

    def __init__(self, base_data):
        """
        Initializes the FinancialModel with base financial data.
        :param base_data: A pandas DataFrame with the base financial data.
        """
        self.base_data = base_data.copy()
        self.base_budget_year1 = self.base_data[self.base_data['Year'] == 'Year_1']['Net_Revenue_Budget'].values[0]
        self.years = 5

    def run_mtfs_projection(self,
                          council_tax_increase_pct,
                          business_rates_growth_pct,
                          grant_change_pct,
                          fees_charges_growth_pct,
                          pay_award_pct,
                          general_inflation_pct,
                          asc_demand_growth_pct,
                          csc_demand_growth_pct,
                          annual_savings_target_pct,
                          use_of_reserves_pct,
                          protect_social_care=False):
        """
        Project full MTFS forward over 5 years.
        
        Returns DataFrame with year-by-year projections and cumulative gap.
        """
        
        results = []
        
        # Convert base data to dict for easier manipulation
        base_dict = self.base_data.set_index('Year').to_dict('index')
        
        cumulative_gap = 0.0
        current_reserves = base_dict['Year_1']['Opening_Reserves']
        
        for year_idx in range(1, self.years + 1):
            year_key = f'Year_{year_idx}'
            year_data = base_dict[year_key]
            
            # === FUNDING SIDE ===
            
            # Council Tax adjusted
            council_tax_base = year_data['Council_Tax_Income']
            council_tax_adjusted = council_tax_base * (1 + council_tax_increase_pct / 100)
            
            # Business Rates adjusted
            business_rates_base = year_data['Business_Rates_Income']
            business_rates_adjusted = business_rates_base * (1 + business_rates_growth_pct / 100)
            
            # Grants adjusted
            grants_base = year_data['Core_Grants']
            grants_adjusted = grants_base * (1 + grant_change_pct / 100)
            
            # Fees & Charges adjusted
            fees_base = year_data['Fees_And_Charges']
            fees_adjusted = fees_base * (1 + fees_charges_growth_pct / 100)
            
            total_funding = (council_tax_adjusted + business_rates_adjusted + 
                           grants_adjusted + fees_adjusted)
            
            # === EXPENDITURE SIDE ===
            
            # Base expenditure
            base_expenditure = year_data['Service_Expenditure']
            
            # Pay impact
            pay_cost_base = year_data['Pay_Cost_Base']
            pay_impact = pay_cost_base * (pay_award_pct / 100)
            
            # Inflation impact
            inflation_base = year_data['Inflation_Base']
            inflation_impact = inflation_base * (general_inflation_pct / 100)
            
            # Demand pressures - Adult Social Care
            asc_base = year_data['Demand_Base_ASC']
            asc_impact = asc_base * (asc_demand_growth_pct / 100)
            
            # Demand pressures - Children's Social Care
            csc_base = year_data['Demand_Base_CSC']
            csc_impact = csc_base * (csc_demand_growth_pct / 100)
            
            # Apply protection to social care if enabled
            if protect_social_care:
                # Hide demand pressures for planning purposes (service continuation)
                asc_impact = 0  # Require must be met from base
                csc_impact = 0  # Require must be met from base
            
            # Total pressures before savings
            total_pressures = pay_impact + inflation_impact + asc_impact + csc_impact
            
            # Savings target applied
            base_expenditure_with_savings = base_expenditure + total_pressures
            annual_savings = base_expenditure_with_savings * (annual_savings_target_pct / 100)
            
            # Final projected expenditure
            mrp_cost = year_data['MRP_Cost']
            interest_cost = year_data['Interest_Cost']
            projected_expenditure = base_expenditure_with_savings - annual_savings + mrp_cost + interest_cost
            
            # === BUDGET GAP ===
            
            annual_budget_gap = projected_expenditure - total_funding
            gap_funded_from_reserves = annual_budget_gap
            
            # Cumulative tracking
            cumulative_gap += annual_budget_gap
            closing_reserves = current_reserves - gap_funded_from_reserves
            
            # Store results
            results.append({
                'Year': year_key,
                'Year_Number': year_idx,
                'Council_Tax_Income': council_tax_adjusted,
                'Business_Rates_Income': business_rates_adjusted,
                'Core_Grants': grants_adjusted,
                'Fees_And_Charges': fees_adjusted,
                'Total_Funding': total_funding,
                'Base_Expenditure': base_expenditure,
                'Pay_Impact': pay_impact,
                'Inflation_Impact': inflation_impact,
                'ASC_Demand_Impact': asc_impact,
                'CSC_Demand_Impact': csc_impact,
                'Annual_Savings': annual_savings,
                'MRP_Cost': mrp_cost,
                'Interest_Cost': interest_cost,
                'Projected_Expenditure': projected_expenditure,
                'Annual_Budget_Gap': annual_budget_gap,
                'Cumulative_Gap': cumulative_gap,
                'Opening_Reserves': current_reserves,
                'Closing_Reserves': closing_reserves,
            })
            
            # Update for next iteration
            current_reserves = closing_reserves
        
        return pd.DataFrame(results)

    def calculate_kpis(self, projection_df, base_budget):
        """
        Calculate headline KPIs from projection.
        """
        
        total_4_year_gap = projection_df['Annual_Budget_Gap'].sum()
        
        # Find year reserves exhausted
        year_exhausted = None
        for _, row in projection_df.iterrows():
            if row['Closing_Reserves'] <= 0:
                year_exhausted = row['Year_Number']
                break
        
        # Savings required to balance (4-year cumulative gap divided by 4)
        savings_required_pct = (total_4_year_gap / base_budget / 4) * 100 if base_budget > 0 else 0
        
        # Council tax equivalent (impact of 1% CT increase)
        council_tax_equivalent = base_budget * 0.01 * 1.0  # 1% of budget ~= CT raises
        
        return {
            'total_4_year_gap': total_4_year_gap,
            'year_reserves_exhausted': year_exhausted,
            'savings_required_pct': savings_required_pct,
            'council_tax_equivalent_impact': council_tax_equivalent,
        }

    def calculate_drivers_waterfall(self, projection_df, baseline_funding):
        """
        Calculate waterfall view of budget gap drivers for Year 1.
        """
        year1 = projection_df[projection_df['Year_Number'] == 1].iloc[0]
        
        # Waterfall drivers
        drivers = {
            'Starting_Funding': baseline_funding,
            'Council_Tax_Growth': year1['Council_Tax_Income'] - baseline_funding * 0.48,
            'Business_Rates_Change': year1['Business_Rates_Income'] - baseline_funding * 0.24,
            'Grant_Changes': year1['Core_Grants'] - baseline_funding * 0.22,
            'Fees_Growth': year1['Fees_And_Charges'] - baseline_funding * 0.06,
            'Pay_Pressures': -year1['Pay_Impact'],
            'Inflation_Pressures': -year1['Inflation_Impact'],
            'Demand_Pressures': -(year1['ASC_Demand_Impact'] + year1['CSC_Demand_Impact']),
            'Savings_Delivered': year1['Annual_Savings'],
        }
        
        return drivers

    def calculate_cipfa_indicators(self, projection_df):
        """
        Calculate CIPFA resilience indicators from projection.
        """
        
        # Financing costs to net revenue stream
        projection_df['Financing_Costs'] = projection_df['MRP_Cost'] + projection_df['Interest_Cost']
        projection_df['Financing_Costs_to_Net_Revenue_Stream_Pct'] = (projection_df['Financing_Costs'] / projection_df['Total_Funding']) * 100
        
        # Change in reserves
        projection_df['Change_in_Reserves'] = projection_df['Closing_Reserves'] - projection_df['Opening_Reserves']
        
        # Capital programme sustainability score (placeholder)
        projection_df['Capital_Programme_Sustainability_Score'] = np.random.uniform(1, 5, len(projection_df))
        
        return projection_df

    def calculate_revenue_impact_bridge(self, initial_gap, mrp_impact, interest_impact):
        """
        Calculates the data for the revenue impact bridge waterfall chart.
        """
        
        bridge_data = {
            'Initial Gap': initial_gap,
            'MRP Impact': mrp_impact,
            'Interest Impact': interest_impact,
        }
        
        return bridge_data
