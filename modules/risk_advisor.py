"""
Risk & Sensitivity-Weighted Scenario Advisor
Links corporate risk register to MTFS sensitivity and recommends stress tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import pandas as pd

REQUIRED_COLUMNS = {
    'risk_id',
    'risk_title',
    'driver_param',
    'driver_label',
    'direction',
    'likelihood',
    'impact',
    'default_stress_pct',
    'risk_owner',
    'notes',
}

DIRECTION_VALUES = {'increase', 'decrease'}

SUGGESTED_ACTIONS = {
    'pay_award_pct': "Set pay contingency; refresh workforce plan; tighten vacancy controls.",
    'general_inflation_pct': "Re-price contracts; strengthen inflation contingency; reduce discretionary spend.",
    'asc_demand_growth_pct': "Activate demand management; review placements; expand reablement capacity.",
    'csc_demand_growth_pct': "Review placement strategy; strengthen edge-of-care support; limit agency usage.",
    'grant_change_pct': "Reassess discretionary budgets; prepare lobbying/negotiation strategy.",
    'business_rates_growth_pct': "Refresh NNDR forecasts; update appeals provision; plan mitigation savings.",
    'council_tax_increase_pct': "Prepare savings fallback; assess referendum capacity and timing.",
    'fees_charges_growth_pct': "Revisit tariff assumptions; test demand elasticity; improve collection.",
    'annual_savings_target_pct': "Strengthen savings governance; identify alternative options pipeline.",
}


@dataclass
class StressResult:
    base_gap: float
    stressed_gap: float
    gap_delta: float
    base_value: float
    stressed_value: float


def load_risk_register(path: Path) -> pd.DataFrame:
    if path.exists():
        df = pd.read_csv(path)
        return normalize_risk_register(df)
    return default_risk_register()


def default_risk_register() -> pd.DataFrame:
    """Load default register from packaged CSV if available."""
    default_path = Path(__file__).parent.parent / 'data' / 'risk_register.csv'
    if default_path.exists():
        return normalize_risk_register(pd.read_csv(default_path))
    # Fallback minimal register
    return normalize_risk_register(pd.DataFrame([
        {
            'risk_id': 'R1',
            'risk_title': 'Pay award pressure',
            'driver_param': 'pay_award_pct',
            'driver_label': 'Pay award %',
            'direction': 'increase',
            'likelihood': 4,
            'impact': 4,
            'default_stress_pct': 20,
            'risk_owner': 'HR/Finance',
            'notes': 'National pay settlement above plan',
        }
    ]))


def normalize_risk_register(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    missing = REQUIRED_COLUMNS.difference(df.columns)
    for col in missing:
        df[col] = ""

    for col in ['likelihood', 'impact', 'default_stress_pct']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['direction'] = df['direction'].astype(str).str.lower().str.strip()
    df.loc[~df['direction'].isin(DIRECTION_VALUES), 'direction'] = 'increase'

    df['risk_score'] = df['likelihood'].clip(0, 5) * df['impact'].clip(0, 5)
    return df


def stress_pct_for_score(risk_score: float) -> float:
    if risk_score >= 20:
        return 25.0
    if risk_score >= 15:
        return 20.0
    if risk_score >= 10:
        return 15.0
    if risk_score >= 6:
        return 10.0
    return 5.0


def _delta_for_value(base_value: float, stress_pct: float) -> float:
    if base_value == 0:
        return stress_pct / 100.0
    return abs(base_value) * (stress_pct / 100.0)


def adverse_value(base_value: float, direction: str, stress_pct: float) -> float:
    delta = _delta_for_value(base_value, stress_pct)
    if direction == 'decrease':
        return base_value - delta
    return base_value + delta


def compute_stress_result(calculator, base_params: Dict[str, float], driver_param: str,
                           direction: str, stress_pct: float) -> StressResult:
    base_gap = calculator.project_mtfs(**base_params)['Annual_Budget_Gap'].sum()
    base_value = base_params.get(driver_param, 0.0)
    stressed_params = base_params.copy()
    stressed_params[driver_param] = adverse_value(base_value, direction, stress_pct)
    stressed_gap = calculator.project_mtfs(**stressed_params)['Annual_Budget_Gap'].sum()
    gap_delta = stressed_gap - base_gap
    return StressResult(
        base_gap=base_gap,
        stressed_gap=stressed_gap,
        gap_delta=gap_delta,
        base_value=base_value,
        stressed_value=stressed_params[driver_param],
    )


def build_stress_table(calculator, base_params: Dict[str, float], risk_df: pd.DataFrame,
                        stress_pct_override: float | None = None) -> pd.DataFrame:
    rows = []
    for _, risk in risk_df.iterrows():
        driver_param = risk['driver_param']
        if driver_param not in base_params:
            continue
        risk_score = float(risk.get('risk_score', 0))
        stress_pct = float(risk.get('default_stress_pct', 0))
        if stress_pct_override is not None:
            stress_pct = stress_pct_override
        if stress_pct <= 0:
            stress_pct = stress_pct_for_score(risk_score)

        result = compute_stress_result(
            calculator=calculator,
            base_params=base_params,
            driver_param=driver_param,
            direction=risk['direction'],
            stress_pct=stress_pct,
        )

        rows.append({
            'Risk ID': risk['risk_id'],
            'Risk': risk['risk_title'],
            'Owner': risk.get('risk_owner', ''),
            'Driver Param': driver_param,
            'Driver': risk.get('driver_label', driver_param),
            'Direction': risk['direction'],
            'Likelihood': risk['likelihood'],
            'Impact': risk['impact'],
            'Risk Score': risk_score,
            'Stress %': stress_pct,
            'Base Value': result.base_value,
            'Stressed Value': result.stressed_value,
            'Gap Delta (£m)': result.gap_delta,
            'Base Gap (£m)': result.base_gap,
            'Stressed Gap (£m)': result.stressed_gap,
            'Weighted Impact': abs(result.gap_delta) * risk_score,
            'Notes': risk.get('notes', ''),
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(['Weighted Impact', 'Risk Score'], ascending=False).reset_index(drop=True)
    return df


def merge_sensitivity(risk_df: pd.DataFrame, sensitivity_df: pd.DataFrame) -> pd.DataFrame:
    if sensitivity_df.empty:
        risk_df['Sensitivity Range (£m)'] = 0.0
        return risk_df

    mapping = {
        row['Assumption']: row['Range (£m)']
        for _, row in sensitivity_df.iterrows()
    }

    def to_label(param: str) -> str:
        return param.replace('_pct', '').replace('_', ' ').title()

    risk_df = risk_df.copy()
    risk_df['Sensitivity Range (£m)'] = risk_df['driver_param'].map(lambda p: mapping.get(to_label(p), 0.0))
    return risk_df


def build_contingency_plan(risk_df: pd.DataFrame) -> pd.DataFrame:
    risk_df = risk_df.copy()
    driver_col = 'driver_param' if 'driver_param' in risk_df.columns else 'Driver Param'
    risk_df['Recommended Action'] = risk_df[driver_col].map(
        lambda p: SUGGESTED_ACTIONS.get(p, "Review mitigation and contingency options.")
    )
    return risk_df
