"""
MTFS Budget Gap Simulator - Risk Assessment (RAG Rating)
Automated resilience and sustainability framework.
"""


class RAGRating:
    """
    Provides automated Red-Amber-Green (RAG) ratings based on financial sustainability rules.
    """
    
    # Configuration thresholds
    MIN_RESERVES_PCT = 5.0  # Minimum reserves as % of net budget
    MAX_GAP_PCT = 8.0  # Maximum tolerable gap as % of budget before RED
    RESERVES_DECLINE_TRIGGER = 25.0  # If reserves decline >25% year-on-year = AMBER
    MAX_SAVINGS_PCT = 5.0  # Maximum realistic savings as % of budget
    
    @staticmethod
    def get_rating(projection_df, base_budget, final_reserves_pct):
        """
        Calculate overall RAG rating.
        
        Args:
            projection_df: Projection DataFrame
            base_budget: Net revenue budget (Year 1)
            final_reserves_pct: Closing reserves as % of budget (Year 5)
        
        Returns:
            Tuple: (rating, reasoning)
        """
        
        red_flags = []
        amber_flags = []
        
        # Rule 1: Reserves depletion
        min_close_reserves = projection_df['Closing_Reserves'].min()
        if min_close_reserves <= 0:
            red_flags.append(f"Reserves exhausted by Year {projection_df[projection_df['Closing_Reserves'] <= 0].iloc[0]['Year_Number']}")
        elif final_reserves_pct < RAGRating.MIN_RESERVES_PCT:
            red_flags.append(f"Reserves fall below {RAGRating.MIN_RESERVES_PCT}% threshold ({final_reserves_pct:.1f}%)")
        
        # Rule 2: Gap sustainability
        avg_annual_gap = projection_df['Annual_Budget_Gap'].mean()
        avg_gap_pct = (avg_annual_gap / base_budget) * 100
        if avg_gap_pct > RAGRating.MAX_GAP_PCT:
            red_flags.append(f"Avg annual gap ({avg_gap_pct:.1f}% of budget) exceeds {RAGRating.MAX_GAP_PCT}%")
        elif avg_gap_pct > (RAGRating.MAX_GAP_PCT * 0.6):
            amber_flags.append(f"Avg annual gap ({avg_gap_pct:.1f}%) approaching threshold")
        
        # Rule 3: Reserves volatility
        reserves_decline = ((projection_df['Opening_Reserves'].iloc[0] - 
                            projection_df['Closing_Reserves'].iloc[-1]) / 
                           projection_df['Opening_Reserves'].iloc[0] * 100)
        if reserves_decline > RAGRating.RESERVES_DECLINE_TRIGGER:
            amber_flags.append(f"Reserves decline {reserves_decline:.1f}% > {RAGRating.RESERVES_DECLINE_TRIGGER}%")
        
        # Rule 4: Savings capacity check
        max_annual_savings = projection_df['Annual_Savings'].max()
        max_savings_pct = (max_annual_savings / base_budget) * 100
        if max_savings_pct > RAGRating.MAX_SAVINGS_PCT:
            amber_flags.append(f"Savings target ({max_savings_pct:.1f}%) at limit of deliverability")
        
        # Overall rating
        if red_flags:
            rating = 'RED'
            reasoning = ' | '.join(red_flags)
        elif amber_flags:
            rating = 'AMBER'
            reasoning = ' | '.join(amber_flags)
        else:
            rating = 'GREEN'
            reasoning = 'Financial position sustainable'
        
        return rating, reasoning
    
    @staticmethod
    def calculate_sustainability_metrics(projection_df, base_budget):
        """
        Calculate financial sustainability indicators.
        """
        final_year = projection_df.iloc[-1]
        
        reserves_to_budget = (final_year['Closing_Reserves'] / base_budget) * 100
        
        avg_annual_savings = projection_df['Annual_Savings'].mean()
        savings_as_pct_budget = (avg_annual_savings / base_budget) * 100
        
        # Funding volatility = std dev of annual funding changes
        funding_changes = projection_df['Total_Funding'].diff().std()
        volatility_score = (funding_changes / base_budget) * 100
        
        return {
            'reserves_to_budget_pct': reserves_to_budget,
            'savings_as_pct_budget': savings_as_pct_budget,
            'funding_volatility_score': volatility_score,
        }

    @staticmethod
    def commercial_rag(project, base_budget, pwlb_rate_pct, invest_threshold_pct=5.0):
        """
        Returns RAG rating and reasoning for a commercial project.

        Rules (default):
        - RED: project.capital_cost > invest_threshold_pct% of base_budget OR spread < 0
        - AMBER: spread < 2% above borrowing cost
        - GREEN: spread >= 2% and capital exposure acceptable
        """
        reasons = []
        exposure_pct = (project.capital_cost / base_budget) * 100 if base_budget else 0.0
        sens = project.sensitivity_summary(pwlb_rate_pct)
        # use pessimistic (60%) net return for safety
        net60 = sens['60%']['net_return']
        spread60 = sens['60%']['spread_pct']

        if exposure_pct > invest_threshold_pct:
            reasons.append(f"Capital exposure {exposure_pct:.1f}% > {invest_threshold_pct}%")
        if spread60 < 0 or net60 < 0:
            reasons.append(f"Pessimistic net return negative (net £{net60:.2f}m, spread {spread60:.2f}%)")
        elif spread60 < 2.0:
            reasons.append(f"Pessimistic spread {spread60:.2f}% < 2% margin")

        if any('negative' in r or exposure_pct > invest_threshold_pct for r in reasons):
            rating = 'RED'
        elif any('margin' in r for r in reasons) or (0 < spread60 < 2.0):
            rating = 'AMBER'
        else:
            rating = 'GREEN'

        return rating, ' | '.join(reasons) if reasons else 'Meets commercial thresholds'
