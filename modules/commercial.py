"""
Commercial project modelling utilities.

Provides deterministic calculations for capital, debt service (MRP),
income realisation sensitivity, and net return vs borrowing cost.
"""
from dataclasses import dataclass
from typing import Dict
import math


@dataclass
class CommercialProject:
    name: str
    capital_cost: float  # £m
    annual_income_target: float  # £m
    life_years: int = 25
    operating_costs: float = 0.0  # £m per year
    capital_receipt: float = 0.0  # one-off capital receipt (£m)

    def annual_debt_service(self, pwlb_rate_pct: float) -> float:
        """
        Calculate annual debt service using annuity formula (principal in £m).
        pwlb_rate_pct is percentage (e.g., 5.0 for 5%).
        """
        P = self.capital_cost
        r = pwlb_rate_pct / 100.0
        n = max(1, int(self.life_years))
        if r <= 0:
            return P / n
        # annuity payment
        annuity = P * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        return annuity

    def projected_income(self, realisation_pct: float) -> float:
        return self.annual_income_target * (realisation_pct / 100.0)

    def net_return(self, realisation_pct: float, pwlb_rate_pct: float) -> Dict[str, float]:
        """
        Returns a dict with income, debt_service, operating_costs, net_return (all £m), and spread vs pwlb.
        """
        income = self.projected_income(realisation_pct)
        debt = self.annual_debt_service(pwlb_rate_pct)
        net = income - debt - self.operating_costs
        roi_pct = (income / self.capital_cost * 100.0) if self.capital_cost else 0.0
        spread = roi_pct - pwlb_rate_pct
        return {
            'income': income,
            'debt_service': debt,
            'operating_costs': self.operating_costs,
            'net_return': net,
            'roi_pct': roi_pct,
            'spread_pct': spread,
        }

    def sensitivity_summary(self, pwlb_rate_pct: float):
        # return net returns for 60%, 80%, 100% realisation
        return {
            '60%': self.net_return(60.0, pwlb_rate_pct),
            '80%': self.net_return(80.0, pwlb_rate_pct),
            '100%': self.net_return(100.0, pwlb_rate_pct),
        }
