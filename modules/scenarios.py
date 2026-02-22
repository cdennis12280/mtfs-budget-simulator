"""
MTFS Budget Gap Simulator - Scenario Definitions
Predefined scenarios for strategic decision support.
"""


class Scenarios:
    """
    Provides predefined financial scenarios.
    """
    
    @staticmethod
    def get_base_case():
        """
        BASE CASE: Moderate growth, realistic inflation, planned savings achieved.
        """
        return {
            'name': 'Base Case',
            'description': 'Moderate funding growth, inflation at target, planned savings delivered',
            'council_tax_increase_pct': 2.0,
            'business_rates_growth_pct': -1.0,
            'grant_change_pct': -2.0,
            'fees_charges_growth_pct': 3.0,
            'pay_award_pct': 3.5,
            'general_inflation_pct': 2.0,
            'asc_demand_growth_pct': 4.0,
            'csc_demand_growth_pct': 3.0,
            'annual_savings_target_pct': 2.0,
            'use_of_reserves_pct': 50.0,
            'protect_social_care': False,
        }
    
    @staticmethod
    def get_optimistic_case():
        """
        OPTIMISTIC: Strong funding growth, lower inflation, savings exceed target.
        """
        return {
            'name': 'Optimistic',
            'description': 'Strong funding growth, inflation below target, higher savings delivery',
            'council_tax_increase_pct': 3.5,
            'business_rates_growth_pct': 2.0,
            'grant_change_pct': 0.5,
            'fees_charges_growth_pct': 5.0,
            'pay_award_pct': 2.5,
            'general_inflation_pct': 1.5,
            'asc_demand_growth_pct': 2.0,
            'csc_demand_growth_pct': 1.5,
            'annual_savings_target_pct': 3.0,
            'use_of_reserves_pct': 25.0,
            'protect_social_care': False,
        }
    
    @staticmethod
    def get_pessimistic_case():
        """
        PESSIMISTIC: Funding decline, high inflation, demand pressures unmet, savings shortfall.
        """
        return {
            'name': 'Pessimistic',
            'description': 'Funding decline, high inflation, demand pressures rise, savings underachieved',
            'council_tax_increase_pct': 1.5,
            'business_rates_growth_pct': -3.0,
            'grant_change_pct': -5.0,
            'fees_charges_growth_pct': 1.0,
            'pay_award_pct': 5.0,
            'general_inflation_pct': 4.5,
            'asc_demand_growth_pct': 6.5,
            'csc_demand_growth_pct': 5.5,
            'annual_savings_target_pct': 1.0,
            'use_of_reserves_pct': 100.0,
            'protect_social_care': True,
        }
    
    @staticmethod
    def get_all_scenarios():
        """Return all predefined scenarios."""
        return {
            'Base Case': Scenarios.get_base_case(),
            'Optimistic': Scenarios.get_optimistic_case(),
            'Pessimistic': Scenarios.get_pessimistic_case(),
        }
