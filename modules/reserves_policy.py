"""
Reserves Policy Alignment Module
Check financial forecasts against council's reserves policy thresholds
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict

@dataclass
class ReservesPolicy:
    """Council's reserves policy parameters"""
    min_pct: float    # Minimum reserves as % of budget (e.g., 5%)
    target_pct: float # Target reserves as % of budget (e.g., 10%)
    max_pct: float    # Maximum reserves as % of budget (e.g., 25%)
    policy_name: str = "Standard Policy"

class ReservesPolicyChecker:
    """Check reserves forecast against policy thresholds"""
    
    def __init__(self, policy: ReservesPolicy = None):
        """
        Args:
            policy: ReservesPolicy instance. Defaults to standard S151 policy.
        """
        if policy is None:
            # Default standard UK local authority policy
            policy = ReservesPolicy(min_pct=5.0, target_pct=10.0, max_pct=25.0, policy_name="Standard S151 Policy")
        self.policy = policy
    
    def check_forecast(self, projection_df: pd.DataFrame, base_budget_year1: float) -> Dict:
        """
        Check if reserves forecast complies with policy.
        
        Args:
            projection_df: MTFS projection DataFrame with Closing_Reserves column
            base_budget_year1: Year 1 budget in £m
        
        Returns:
            Dict with compliance status for each year
        """
        results = {
            'policy': self.policy,
            'by_year': [],
            'compliant': True,
            'min_breach_year': None,
            'max_breach_year': None,
        }
        
        min_threshold = base_budget_year1 * (self.policy.min_pct / 100.0)
        target_threshold = base_budget_year1 * (self.policy.target_pct / 100.0)
        max_threshold = base_budget_year1 * (self.policy.max_pct / 100.0)
        
        for idx, row in projection_df.iterrows():
            closing_reserves = row['Closing_Reserves']
            year = row['Year_Number']
            reserves_pct = (closing_reserves / base_budget_year1) * 100
            
            # Determine status
            if closing_reserves < min_threshold:
                status = 'RED'  # Below minimum
                results['compliant'] = False
                if results['min_breach_year'] is None:
                    results['min_breach_year'] = year
            elif closing_reserves < target_threshold:
                status = 'AMBER'  # Below target but above minimum
            elif closing_reserves > max_threshold:
                status = 'AMBER'  # Above maximum (overfunded)
                if results['max_breach_year'] is None:
                    results['max_breach_year'] = year
            else:
                status = 'GREEN'  # Ideal range
            
            results['by_year'].append({
                'year': year,
                'closing_reserves': closing_reserves,
                'reserves_pct': reserves_pct,
                'min_threshold': min_threshold,
                'target_threshold': target_threshold,
                'max_threshold': max_threshold,
                'status': status,
            })
        
        return results
    
    def summary_text(self, check_results: Dict) -> str:
        """Generate friendly summary text of policy compliance"""
        if check_results['compliant']:
            return f"✅ Reserves forecast complies with {check_results['policy'].policy_name}"
        elif check_results['min_breach_year']:
            return f"⚠️ WARNING: Reserves fall below minimum ({check_results['policy'].min_pct}%) in Year {check_results['min_breach_year']}"
        else:
            return "⚠️ Policy compliance issues detected"
    
    def recommendation_text(self, check_results: Dict, base_budget_year1: float) -> str:
        """Generate S151 recommendation based on policy check"""
        target_reserves = base_budget_year1 * (self.policy.target_pct / 100.0)
        
        if check_results['compliant']:
            return f"Reserves policy met. Target position is £{target_reserves:.1f}m ({self.policy.target_pct}% of budget)."
        elif check_results['min_breach_year']:
            return (
                f"Reserves fall below statutory minimum ({self.policy.min_pct}%) in Year {check_results['min_breach_year']}. "
                f"Recommend increasing savings targets or reducing use of reserves to maintain £{base_budget_year1 * (self.policy.min_pct / 100.0):.1f}m minimum."
            )
        else:
            return "Review reserves management strategy to ensure compliance."
