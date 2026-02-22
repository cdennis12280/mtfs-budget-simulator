"""
Sensitivity Analysis
Tornado chart and one-way sensitivity for MTFS assumptions
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

class SensitivityAnalysis:
    """Compute sensitivity of cumulative gap to individual assumption changes."""
    
    def __init__(self, calculator, base_data, base_budget_year1):
        """
        Args:
            calculator: MTFSCalculator instance
            base_data: Pandas DataFrame with base financials
            base_budget_year1: Float, Year 1 budget
        """
        self.calculator = calculator
        self.base_data = base_data
        self.base_budget_year1 = base_budget_year1
    
    def compute_base_gap(self, **kwargs):
        """Run model with given parameters and return 4-year cumulative gap."""
        proj = self.calculator.project_mtfs(**kwargs)
        return proj['Annual_Budget_Gap'].sum()
    
    def tornado_analysis(self, base_params: dict, perturbation_pct: float = 10.0) -> pd.DataFrame:
        """
        Compute tornado chart data: show impact of ±perturbation_pct on each assumption.
        
        Args:
            base_params: dict of base assumption values
            perturbation_pct: % change to apply (e.g., 10 = ±10%)
        
        Returns:
            DataFrame with columns: [Assumption, Low Impact, High Impact, Range]
        """
        base_gap = self.compute_base_gap(**base_params)
        
        results = []
        param_names = [
            'council_tax_increase_pct',
            'business_rates_growth_pct',
            'grant_change_pct',
            'fees_charges_growth_pct',
            'pay_award_pct',
            'general_inflation_pct',
            'asc_demand_growth_pct',
            'csc_demand_growth_pct',
            'annual_savings_target_pct',
        ]
        
        for param in param_names:
            if param not in base_params:
                continue
            
            base_val = base_params[param]
            delta = abs(base_val) * (perturbation_pct / 100.0) if base_val != 0 else perturbation_pct / 100.0
            
            # Compute low / high scenarios
            params_low = base_params.copy()
            params_low[param] = base_val - delta
            gap_low = self.compute_base_gap(**params_low)
            
            params_high = base_params.copy()
            params_high[param] = base_val + delta
            gap_high = self.compute_base_gap(**params_high)
            
            # Impact on gap (higher gap = worse)
            impact_low = gap_low - base_gap
            impact_high = gap_high - base_gap
            
            # For display, order by range magnitude (tornado shape)
            range_impact = abs(impact_high - impact_low)
            
            # Friendly label
            label = param.replace('_pct', '').replace('_', ' ').title()
            
            results.append({
                'Assumption': label,
                'Low Impact (£m)': impact_low,
                'High Impact (£m)': impact_high,
                'Range (£m)': range_impact,
            })
        
        df = pd.DataFrame(results)
        # Sort by range descending (biggest sensitivity first)
        df = df.sort_values('Range (£m)', ascending=False).reset_index(drop=True)
        return df
    
    def plot_tornado(self, sensitivity_df: pd.DataFrame, template: str = 'plotly_white') -> go.Figure:
        """Create a tornado chart from sensitivity DataFrame."""
        x0 = sensitivity_df['Low Impact (£m)'].values
        x1 = sensitivity_df['High Impact (£m)'].values
        y = sensitivity_df['Assumption'].values
        
        # Compute center point and ranges for tornado shape
        centers = (x0 + x1) / 2
        ranges = np.abs(x1 - x0) / 2
        
        fig = go.Figure()
        
        # Add bars for low and high
        fig.add_trace(go.Bar(
            y=y,
            x=x0 - centers,
            name='Low Scenario',
            orientation='h',
            marker=dict(color='#d62728')
        ))
        
        fig.add_trace(go.Bar(
            y=y,
            x=x1 - centers,
            name='High Scenario',
            orientation='h',
            marker=dict(color='#2ca02c')
        ))
        
        fig.update_layout(
            title='Sensitivity Tornado: Impact on Cumulative 4-Year Gap (£m)',
            xaxis_title='Gap Impact (£m) — Red/Left = Worse, Green/Right = Better',
            yaxis_title='Assumption',
            barmode='relative',
            height=500,
            hovermode='closest',
            template=template,
        )
        
        return fig
